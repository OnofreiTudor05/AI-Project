class Piece:
    def __init__(self, color, type_, image, killable, occupied, row_, column, width):
        self.info = {'color': color, 'image': image, 'type': type_, 'killable': killable, 'occupied': occupied,
                     'row': row_, 'column': column, 'x': int(width * row_), 'y': int(width * column)}

    def update(self, field, value):
        self.info[field] = value
