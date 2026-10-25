# the concepts of minimax and negamax

INF = float("inf")

TREE = [
    [[3, 5], [6, 9]],
    [[1, 2], [0, -1]],
]

visited = []
visited_negamax = []
alpha = -INF
beta = INF
color = 1
depth = 3
player = "maximising"
def minimax(node, alpha, beta, depth, player):
    if depth == 0:
        visited.append(node)
        return node
    best_score = 1000 if player =="minimising" else -1000
    next_player = "minimising" if player == "maximising" else "maximising"
    for child in node:
        score = minimax(child, alpha, beta, depth-1, next_player)
        if player == "maximising":
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        else:
            if score < best_score:
                best_score = score
            if score < beta:
                beta = score
            if beta <= alpha:
                break
        
    return best_score

print(minimax(TREE, alpha, beta, depth, player))
print(visited)

def negamax(node, alpha, beta, depth, color):
    if depth == 0:
        visited_negamax.append(node)
        return node * color
    
    best_score = -1000
    for child in node:
        score = -negamax(child, -beta, -alpha, depth-1, -color)
        if score > best_score:
            best_score = score
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    return best_score

print(negamax(TREE, alpha, beta, depth, 1))
print(visited_negamax)