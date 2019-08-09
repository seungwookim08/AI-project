
class BoardPiece:
    def __init__(self, pos_x=-10, pos_y=-10, rot_type=1):
        self.rot_type = rot_type
        if rot_type < 5:
            self.side = 1
        else:
            self.side = 2
        if rot_type is 1 or rot_type is 4 or rot_type is 5 or rot_type is 8:
            self.red_pos_x = pos_x
            self.red_pos_y = pos_y

            if rot_type is 1 or rot_type is 5:
                self.angle = 0
                self.white_pos_x = self.red_pos_x + 1
                self.white_pos_y = self.red_pos_y
            else:
                self.angle = 90
                self.white_pos_x = self.red_pos_x
                self.white_pos_y = self.red_pos_y + 1
        else:
            self.white_pos_x = pos_x
            self.white_pos_y = pos_y

            if rot_type is 3 or rot_type is 7:
                self.angle = 180
                self.red_pos_x = self.white_pos_x + 1
                self.red_pos_y = self.white_pos_y
            else:
                self.angle = 270
                self.red_pos_x = self.white_pos_x
                self.red_pos_y = self.white_pos_y + 1
