def achieve_position(state, obj, target_pos):
    if state.pos[obj] != target_pos:
        return [('move', obj, target_pos)]
    return []  # Already satisfied

gtpyhop.declare_unigoal_methods('pos', achieve_position)