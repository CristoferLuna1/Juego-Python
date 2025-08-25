class GameState:
    def __init__(self):
        self.players = {}
        self.enemies = []
        self.projectiles = []
        self.running = True

    def add_player(self, pid, player):
        self.players[pid] = player

    def remove_player(self, pid):
        if pid in self.players:
            del self.players[pid]

    def check_gameover(player):
        """
        Revisa si el jugador ha perdido el juego.
        Retorna True si está en estado de 'game over'.
        """

        # Si el jugador no tiene salud
        if player.health <= 0:
            return True

        # Si el escudo está destruido (opcional, si lo manejas así)
        if hasattr(player, "shield") and player.shield <= 0:
            return True
        return False

    def update(self, dt):
        for p in self.players.values():
            p.update(dt)
        for e in self.enemies:
            e.update(dt)
        for proj in self.projectiles:
            proj.update(dt)