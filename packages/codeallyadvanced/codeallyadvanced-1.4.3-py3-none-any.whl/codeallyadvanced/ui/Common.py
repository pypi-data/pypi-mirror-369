
from codeallybasic.Position import Position

from codeallyadvanced.ui.AttachmentSide import AttachmentSide


class Common:
    def __init__(self):
        pass

    @classmethod
    def whereIsDestination(cls, sourcePosition: Position, destinationPosition: Position) -> AttachmentSide:
        """
        Given a source and destination positions, this method calculates and returns the destination
        location relative to the source.

        Args:
            sourcePosition:
            destinationPosition:

        Returns: The destination location relative to the source
        """
        sourceX:      int = sourcePosition.x
        sourceY:      int = sourcePosition.y
        destinationX: int = destinationPosition.x
        destinationY: int = destinationPosition.y

        deltaX: int = sourceX - destinationX
        deltaY: int = sourceY - destinationY
        if deltaX > 0:  # destination is not East
            if deltaX > abs(deltaY):  # destination is East
                return AttachmentSide.WEST
            elif deltaY > 0:
                return AttachmentSide.NORTH
            else:
                return AttachmentSide.SOUTH
        else:  # destination is not West
            if -deltaX > abs(deltaY):  # destination is East
                return AttachmentSide.EAST
            elif deltaY > 0:
                return AttachmentSide.NORTH
            else:
                return AttachmentSide.SOUTH
