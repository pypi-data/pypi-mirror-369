"""
Version optimisée du simple_htn.py avec gestion mémoire contrôlée
Utilise unittest pour gérer l'allocation et désallocation des instances State
-- Optimisation par Claude, basée sur le code de Dana Nau
"""

import unittest
import weakref
import gc
import sys
from typing import List, Dict, Any, Optional, Set
from contextlib import contextmanager
import gtpyhop
import random
import gtpyhop.test_harness as th


# Configuration du domaine
domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)


class StateManager:
    """Gestionnaire centralisé pour les instances State avec tracking mémoire"""
    
    def __init__(self):
        self._state_registry: Set[weakref.ref] = set()
        self._creation_count = 0
        self._cleanup_count = 0
    
    def register_state(self, state: gtpyhop.State) -> gtpyhop.State:
        """Enregistre une nouvelle instance State"""
        def cleanup_callback(ref):
            self._state_registry.discard(ref)
            self._cleanup_count += 1
        
        ref = weakref.ref(state, cleanup_callback)
        self._state_registry.add(ref)
        self._creation_count += 1
        return state
    
    def get_active_states_count(self) -> int:
        """Retourne le nombre d'instances State actives"""
        # Nettoie les références mortes
        self._state_registry = {ref for ref in self._state_registry if ref() is not None}
        return len(self._state_registry)
    
    def force_cleanup(self):
        """Force le nettoyage des instances State"""
        gc.collect()
        self._state_registry = {ref for ref in self._state_registry if ref() is not None}
    
    def get_stats(self) -> Dict[str, int]:
        """Retourne les statistiques d'allocation"""
        return {
            'created': self._creation_count,
            'cleaned': self._cleanup_count,
            'active': self.get_active_states_count()
        }
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self._creation_count = 0
        self._cleanup_count = 0
        self.force_cleanup()


# Instance globale du gestionnaire d'états
state_manager = StateManager()


class ManagedState(gtpyhop.State):
    """Version de State avec gestion mémoire automatique"""
    
    def __init__(self, name: str = 'managed_state'):
        super().__init__(name)
        self.name = name  # Initialize the name attribute
        state_manager.register_state(self)
    
    def copy(self) -> 'ManagedState':
        """Copie gérée avec tracking automatique"""
        new_state = ManagedState(f"{self.name}_copy")
        
        # Copie des attributs de base
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name != 'name':
                attr_value = getattr(self, attr_name)
                if hasattr(attr_value, 'copy'):
                    setattr(new_state, attr_name, attr_value.copy())
                elif isinstance(attr_value, dict):
                    setattr(new_state, attr_name, attr_value.copy())
                elif isinstance(attr_value, list):
                    setattr(new_state, attr_name, attr_value.copy())
                else:
                    setattr(new_state, attr_name, attr_value)
        
        return new_state


################################################################################
# États et relations rigides

rigid = ManagedState('rigid_relations')
rigid.types = {
    'person':   ['alice', 'bob'],
    'location': ['home_a', 'home_b', 'park', 'station'],
    'taxi':     ['taxi1', 'taxi2']
}
rigid.dist = {
    ('home_a', 'park'): 8,    ('home_b', 'park'): 2,
    ('station', 'home_a'): 1, ('station', 'home_b'): 7,
    ('home_a', 'home_b'): 7,  ('station', 'park'): 9
}


def create_initial_state() -> ManagedState:
    """Factory pour créer l'état initial"""
    state = ManagedState('initial_state')
    state.loc = {'alice': 'home_a', 'bob': 'home_b', 'taxi1': 'park', 'taxi2': 'station'}
    state.cash = {'alice': 20, 'bob': 15}
    state.owe = {'alice': 0, 'bob': 0}
    return state


###############################################################################
# Fonctions utilitaires

def taxi_rate(dist: float) -> float:
    """Calcule le tarif du taxi"""
    return 1.5 + 0.5 * dist


def distance(x: str, y: str) -> Optional[float]:
    """Calcule la distance entre deux locations"""
    return rigid.dist.get((x, y)) or rigid.dist.get((y, x))


def is_a(variable: str, type_name: str) -> bool:
    """Vérifie le type d'une variable"""
    return variable in rigid.types[type_name]


###############################################################################
# Actions

def walk(state: ManagedState, p: str, x: str, y: str) -> Optional[ManagedState]:
    """Action de marche"""
    if is_a(p, 'person') and is_a(x, 'location') and is_a(y, 'location') and x != y:
        if state.loc[p] == x:
            state.loc[p] = y
            return state
    return None


def call_taxi(state: ManagedState, p: str, x: str) -> Optional[ManagedState]:
    """Action d'appel de taxi"""
    if is_a(p, 'person') and is_a(x, 'location'):
        state.loc['taxi1'] = x
        state.loc[p] = 'taxi1'
        return state
    return None


def ride_taxi(state: ManagedState, p: str, y: str) -> Optional[ManagedState]:
    """Action de voyage en taxi"""
    if is_a(p, 'person') and is_a(state.loc[p], 'taxi') and is_a(y, 'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x, 'location') and x != y:
            state.loc[taxi] = y
            state.owe[p] = taxi_rate(distance(x, y))
            return state
    return None


def pay_driver(state: ManagedState, p: str, y: str) -> Optional[ManagedState]:
    """Action de paiement du chauffeur"""
    if is_a(p, 'person'):
        if state.cash[p] >= state.owe[p]:
            state.cash[p] = state.cash[p] - state.owe[p]
            state.owe[p] = 0
            state.loc[p] = y
            return state
    return None


# Déclaration des actions
gtpyhop.declare_actions(walk, call_taxi, ride_taxi, pay_driver)


###############################################################################
# Commandes avec gestion d'erreur

def c_walk(state: ManagedState, p: str, x: str, y: str) -> Optional[ManagedState]:
    """Commande de marche"""
    return walk(state, p, x, y)


def c_call_taxi(state: ManagedState, p: str, x: str) -> Optional[ManagedState]:
    """Commande d'appel de taxi (avec probabilité d'échec)"""
    if is_a(p, 'person') and is_a(x, 'location'):
        if random.randrange(2) > 0:
            state.loc['taxi1'] = x
            state.loc[p] = 'taxi1'
            print('Action> c_call_taxi succeeded. Pr = 1/2')
            return state
        else:
            print('Action> c_call_taxi failed. Pr = 1/2')
            return None
    return None


def c_ride_taxi(state: ManagedState, p: str, y: str) -> Optional[ManagedState]:
    """Commande de voyage en taxi"""
    return ride_taxi(state, p, y)


def c_pay_driver(state: ManagedState, p: str, y: str) -> Optional[ManagedState]:
    """Commande de paiement du chauffeur"""
    return pay_driver(state, p, y)


# Déclaration des commandes
gtpyhop.declare_commands(c_walk, c_call_taxi, c_ride_taxi, c_pay_driver)


###############################################################################
# Méthodes

def do_nothing(state: ManagedState, p: str, y: str) -> Optional[List]:
    """Méthode pour ne rien faire si déjà à destination"""
    if is_a(p, 'person') and is_a(y, 'location'):
        if state.loc[p] == y:
            return []
    return None


def travel_by_foot(state: ManagedState, p: str, y: str) -> Optional[List]:
    """Méthode de voyage à pied"""
    if is_a(p, 'person') and is_a(y, 'location'):
        x = state.loc[p]
        if x != y and distance(x, y) <= 2:
            return [('walk', p, x, y)]
    return None


def travel_by_taxi(state: ManagedState, p: str, y: str) -> Optional[List]:
    """Méthode de voyage en taxi"""
    if is_a(p, 'person') and is_a(y, 'location'):
        x = state.loc[p]
        if x != y and state.cash[p] >= taxi_rate(distance(x, y)):
            return [('call_taxi', p, x), ('ride_taxi', p, y), ('pay_driver', p, y)]
    return None


# Déclaration des méthodes
gtpyhop.declare_task_methods('travel', do_nothing, travel_by_foot, travel_by_taxi)


###############################################################################
# Tests unitaires avec gestion mémoire

class HTNPlanningTestCase(unittest.TestCase):
    """Classe de test avec gestion mémoire optimisée"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration une fois pour toute la classe"""
        gtpyhop.current_domain = the_domain
        print(f"\n=== Début des tests pour le domaine '{domain_name}' ===")
        
    @classmethod
    def tearDownClass(cls):
        """Nettoyage final après tous les tests"""
        state_manager.force_cleanup()
        final_stats = state_manager.get_stats()
        print(f"\n=== Statistiques finales ===")
        print(f"États créés: {final_stats['created']}")
        print(f"États nettoyés: {final_stats['cleaned']}")
        print(f"États actifs: {final_stats['active']}")
        
        if final_stats['active'] > 0:
            print(f"⚠️  Attention: {final_stats['active']} états non nettoyés")
        else:
            print("✅ Tous les états ont été correctement nettoyés")
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.initial_stats = state_manager.get_stats()
        self.test_states = []
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Libère explicitement les références locales
        for state in self.test_states:
            del state
        self.test_states.clear()
        
        # Force le garbage collection
        state_manager.force_cleanup()
        
        # Vérifie les fuites mémoire
        current_stats = state_manager.get_stats()
        created_in_test = current_stats['created'] - self.initial_stats['created']
        cleaned_in_test = current_stats['cleaned'] - self.initial_stats['cleaned']
        
        if created_in_test > 0:
            print(f"Test {self._testMethodName}: {created_in_test} états créés, "
                  f"{cleaned_in_test} nettoyés")
    
    @contextmanager
    def memory_tracking(self, test_name: str):
        """Context manager pour tracker l'utilisation mémoire"""
        before = state_manager.get_stats()
        try:
            yield
        finally:
            state_manager.force_cleanup()
            after = state_manager.get_stats()
            created = after['created'] - before['created']
            cleaned = after['cleaned'] - before['cleaned']
            active = after['active'] - before['active']
            
            if created > 0:
                print(f"  {test_name}: +{created} créés, +{cleaned} nettoyés, "
                      f"{active:+d} actifs")
    
    def create_test_state(self, name: str = None) -> ManagedState:
        """Factory pour créer un état de test géré"""
        state = create_initial_state()
        if name:
            state.name = name
        self.test_states.append(state)
        return state
    
    def test_basic_planning(self):
        """Test de planification de base"""
        with self.memory_tracking("test_basic_planning"):
            state = self.create_test_state("basic_test")
            
            gtpyhop.verbose = 0
            result = gtpyhop.find_plan(state, [('travel', 'alice', 'park')])
            
            expected = [('call_taxi', 'alice', 'home_a'), 
                       ('ride_taxi', 'alice', 'park'), 
                       ('pay_driver', 'alice', 'park')]
            
            self.assertEqual(result, expected)
    
    def test_multiple_travelers(self):
        """Test avec plusieurs voyageurs"""
        with self.memory_tracking("test_multiple_travelers"):
            state = self.create_test_state("multiple_test")
            
            gtpyhop.verbose = 0
            result = gtpyhop.find_plan(state, [('travel', 'alice', 'park'), 
                                               ('travel', 'bob', 'park')])
            
            expected = [('call_taxi', 'alice', 'home_a'),
                       ('ride_taxi', 'alice', 'park'),
                       ('pay_driver', 'alice', 'park'),
                       ('walk', 'bob', 'home_b', 'park')]
            
            self.assertEqual(result, expected)
    
    def test_state_copying(self):
        """Test de copie d'états"""
        with self.memory_tracking("test_state_copying"):
            original = self.create_test_state("original")
            original.cash['alice'] = 100
            
            # Test de copie
            copy1 = original.copy()
            copy2 = original.copy()
            
            # Ajoute les copies à la liste de gestion
            self.test_states.extend([copy1, copy2])
            
            # Vérifie que les copies sont indépendantes
            copy1.cash['alice'] = 50
            copy2.cash['alice'] = 25
            
            self.assertEqual(original.cash['alice'], 100)
            self.assertEqual(copy1.cash['alice'], 50)
            self.assertEqual(copy2.cash['alice'], 25)
    
    def test_no_solution(self):
        """Test avec problème sans solution"""
        with self.memory_tracking("test_no_solution"):
            state = self.create_test_state("no_solution")
            # Enlève tout l'argent
            state.cash = {'alice': 0, 'bob': 0}
            
            gtpyhop.verbose = 0
            result = gtpyhop.find_plan(state, [('travel', 'alice', 'park')])
            
            # Aucune solution possible
            self.assertIsNone(result)
    
    def test_already_at_destination(self):
        """Test quand déjà à destination"""
        with self.memory_tracking("test_already_at_destination"):
            state = self.create_test_state("already_there")
            state.loc['alice'] = 'park'
            
            gtpyhop.verbose = 0
            result = gtpyhop.find_plan(state, [('travel', 'alice', 'park')])
            
            # Plan vide car déjà à destination
            self.assertEqual(result, [])
    
    def test_memory_pressure(self):
        """Test de pression mémoire avec nombreuses copies"""
        with self.memory_tracking("test_memory_pressure"):
            base_state = self.create_test_state("base")
            
            # Crée de nombreuses copies
            copies = []
            for i in range(100):
                copy = base_state.copy()
                copies.append(copy)
                
            # Ajoute à la gestion
            self.test_states.extend(copies)
            
            # Vérifie que toutes les copies sont distinctes
            for i, copy in enumerate(copies):
                copy.cash['alice'] = i
                
            # Vérifie l'indépendance
            values = [copy.cash['alice'] for copy in copies]
            self.assertEqual(values, list(range(100)))
    
    def test_deep_copy_integrity(self):
        """Test de l'intégrité des copies profondes"""
        with self.memory_tracking("test_deep_copy_integrity"):
            original = self.create_test_state("deep_copy_test")
            
            # Modifie les structures imbriquées
            original.complex_data = {
                'nested': {'level1': {'level2': 'value'}},
                'list_data': [1, 2, [3, 4]]
            }
            
            # Crée une copie
            copy = original.copy()
            self.test_states.append(copy)
            
            # Modifie l'original
            original.complex_data['nested']['level1']['level2'] = 'modified'
            original.complex_data['list_data'][2][0] = 999
            
            # Vérifie que la copie n'est pas affectée
            self.assertEqual(copy.complex_data['nested']['level1']['level2'], 'value')
            self.assertEqual(copy.complex_data['list_data'][2][0], 3)
    
    def test_concurrent_planning(self):
        """Test de planification concurrente"""
        with self.memory_tracking("test_concurrent_planning"):
            states = []
            plans = []
            
            # Crée plusieurs états avec des conditions différentes
            for i in range(10):
                state = self.create_test_state(f"concurrent_{i}")
                state.cash['alice'] = 10 + i * 5  # Cash variable
                states.append(state)
            
            # Planifie pour chaque état
            gtpyhop.verbose = 0
            for state in states:
                plan = gtpyhop.find_plan(state, [('travel', 'alice', 'park')])
                plans.append(plan)
            
            # Vérifie que toutes les planifications ont réussi
            for plan in plans:
                self.assertIsNotNone(plan)
                self.assertGreater(len(plan), 0)


class HTNMemoryLeakTestCase(unittest.TestCase):
    """Tests spécifiques pour détecter les fuites mémoire"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        state_manager.reset_stats()
        self.initial_memory = state_manager.get_stats()
    
    def tearDown(self):
        """Vérification après chaque test"""
        state_manager.force_cleanup()
        final_memory = state_manager.get_stats()
        
        # Vérifie qu'il n'y a pas de fuites
        if final_memory['active'] > 0:
            print(f"⚠️  Fuite détectée: {final_memory['active']} états actifs")
    
    def test_massive_state_creation(self):
        """Test de création massive d'états"""
        states = []
        
        try:
            for i in range(1000):
                state = create_initial_state()
                state.test_id = i
                states.append(state)
            
            # Vérifie que tous les états sont créés
            self.assertEqual(len(states), 1000)
            
            # Vérifie l'unicité
            ids = [state.test_id for state in states]
            self.assertEqual(len(set(ids)), 1000)
            
        finally:
            # Nettoyage explicite
            for state in states:
                del state
            del states
            
            # Force le garbage collection
            state_manager.force_cleanup()
    
    def test_recursive_copying(self):
        """Test de copie récursive"""
        def create_copy_chain(state, depth):
            if depth <= 0:
                return []
            
            copy = state.copy()
            copy.depth = depth
            copies = [copy]
            copies.extend(create_copy_chain(copy, depth - 1))
            return copies
        
        original = create_initial_state()
        
        try:
            # Crée une chaîne de copies
            copies = create_copy_chain(original, 50)
            
            # Vérifie la chaîne
            self.assertEqual(len(copies), 50)
            
            # Vérifie que chaque copie a la bonne profondeur
            for i, copy in enumerate(copies):
                expected_depth = 50 - i
                self.assertEqual(copy.depth, expected_depth)
                
        finally:
            # Nettoyage
            for copy in copies:
                del copy
            del copies
            del original
            
            state_manager.force_cleanup()


def run_performance_benchmark():
    """Benchmark de performance avec gestion mémoire"""
    print("\n=== Benchmark de performance ===")
    
    import time
    
    # Réinitialise les statistiques
    state_manager.reset_stats()
    
    start_time = time.time()
    
    # Test de création/copie massive
    base_state = create_initial_state()
    states = []
    
    for i in range(1000):
        if i % 100 == 0:
            print(f"  Création: {i}/1000")
        
        copy = base_state.copy()
        states.append(copy)
        
        # Planification simple
        gtpyhop.verbose = 0
        gtpyhop.find_plan(copy, [('travel', 'alice', 'park')])
    
    end_time = time.time()
    
    # Statistiques finales
    stats = state_manager.get_stats()
    
    print(f"\nRésultats du benchmark:")
    print(f"  Temps total: {end_time - start_time:.2f}s")
    print(f"  États créés: {stats['created']}")
    print(f"  États/seconde: {stats['created'] / (end_time - start_time):.1f}")
    print(f"  États actifs: {stats['active']}")
    
    # Nettoyage final
    del states
    del base_state
    state_manager.force_cleanup()
    
    final_stats = state_manager.get_stats()
    print(f"  États après nettoyage: {final_stats['active']}")


def run_memory_stress_test():
    """Test de stress mémoire"""
    print("\n=== Test de stress mémoire ===")
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # Mémoire initiale
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Mémoire initiale: {initial_memory:.1f} MB")
    
    # Réinitialise les statistiques
    state_manager.reset_stats()
    
    # Crée de nombreux états de façon cyclique
    for cycle in range(10):
        print(f"  Cycle {cycle + 1}/10")
        
        # Crée des états
        states = []
        for i in range(500):
            state = create_initial_state()
            state.cycle = cycle
            state.index = i
            states.append(state)
        
        # Effectue des planifications
        gtpyhop.verbose = 0
        for state in states[:100]:  # Limite pour éviter la surcharge
            gtpyhop.find_plan(state, [('travel', 'alice', 'park')])
        
        # Libère les états
        del states
        
        # Force le nettoyage
        state_manager.force_cleanup()
        
        # Vérifie la mémoire
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"    Mémoire après cycle {cycle + 1}: {current_memory:.1f} MB")
    
    # Statistiques finales
    final_stats = state_manager.get_stats()
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"\nRésultats du stress test:")
    print(f"  Mémoire finale: {final_memory:.1f} MB")
    print(f"  Augmentation: {final_memory - initial_memory:.1f} MB")
    print(f"  États créés: {final_stats['created']}")
    print(f"  États actifs: {final_stats['active']}")
    
    if final_stats['active'] == 0:
        print("✅ Aucune fuite mémoire détectée")
    else:
        print(f"⚠️  {final_stats['active']} états non nettoyés")


def main():
    """Fonction principale pour exécuter les tests"""
    print(f"=== Démarrage des tests HTN avec gestion mémoire ===")
    print(f"Domaine: {domain_name}")
    print(f"Version Python: {sys.version}")
    
    # Exécute les tests unitaires
    print("\n1. Tests unitaires de base:")
    unittest.main(verbosity=2, exit=False, argv=[''])
    
    # Exécute le benchmark
    print("\n2. Benchmark de performance:")
    run_performance_benchmark()
    
    # Exécute le test de stress mémoire
    print("\n3. Test de stress mémoire:")
    run_memory_stress_test()
    
    print("\n=== Fin des tests ===")


if __name__ == '__main__':
    main()
