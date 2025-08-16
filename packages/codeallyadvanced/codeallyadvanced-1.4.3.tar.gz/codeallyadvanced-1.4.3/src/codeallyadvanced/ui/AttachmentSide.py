
from enum import Enum


class AttachmentSide(Enum):
    """
    Cardinal points, taken to correspond to the attachment points of any shape
    in a Cartesian coordinate system.

    """
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

    def __str__(self):
        return str(self.name)

    @staticmethod
    def toEnum(strValue: str) -> 'AttachmentSide':
        """
        Converts the input string to the attachment location
        Args:
            strValue:   A serialized string value

        Returns:  The attachment side enumeration
        """
        canonicalStr: str = strValue.strip(' ')

        if canonicalStr == 'NORTH':
            return AttachmentSide.NORTH
        elif canonicalStr == 'EAST':
            return AttachmentSide.EAST
        elif canonicalStr == 'WEST':
            return AttachmentSide.WEST
        elif canonicalStr == 'SOUTH':
            return AttachmentSide.SOUTH
        else:
            print(f'Warning: did not recognize this attachment point: {canonicalStr}')
            return AttachmentSide.NORTH
