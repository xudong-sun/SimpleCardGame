card_characters = '3456789TJQKA2SB'

def sort_card_string(card_string):
    '''
    card_string: str
    return: str, sorted according to card_characters
    '''
    temp_list = list(card_string)
    temp_list.sort(key=lambda x: card_characters.index(x))
    return ''.join(temp_list)

def get_order(character):
    '''
    character: a card character
    return: int
    '''
    return card_characters.index(character)


def is_shunzi(card_string):
    '''
    return: None (not a shunzi) / int (order of shunzi)
    '''
    orders = [get_order(character) for character in card_string]

    if orders[-1] > 12:
        return None
    if orders[-1] == 12:
        orders = [-1] + orders[0:-1]
    if orders[-1] == 11 and orders[0] == -1:
        orders = [-2] + orders[0:-1]

    for index in range(1, len(orders)):
        if orders[index - 1] != orders[index] - 1:
                return None

    return orders[0]


class CardType(object):
    def __init__(self, display, type_no, order):
        self.display = display
        self.type_no = type_no
        self.order = order

    @staticmethod
    def parse(card_string):
        '''
        card_string: string
        return: CardType / None
        '''
        card_string = card_string.upper()
        for ch in card_string:
            if ch not in card_characters:
                return None

        card_string = sort_card_string(card_string)

        for cls in type_class:
            result = cls.parse(card_string)
            if result is not None:
                return result

    def __gt__(self, card):
        if (self.type_no == card.type_no):
            if ('length' in self.__dict__ and self.length != card.length):
                return False
            if (self.type_no != 10):
                return self.order > card.order
            else:
                return (self.mag, self.order) > (card.mag, card.order)
        else:
            if self.type_no == 10 or card.type_no == -1:
                return True
            else:
                return False

    def __str__(self):
        return self.display

    def display_logic(self):
        return '{}: type_no = {} order = {}'.format(self.__class__.__name__, self.type_no, self.order)


class DanZhang(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) == 1:
            return DanZhang(card_string, 0, get_order(card_string))


class DuiZi(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) == 2 and card_string[0] == card_string[1]:
            return DuiZi(card_string, 1, get_order(card_string[0]))


class GuangSan(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) == 3 and card_string[0] == card_string[1] == card_string[2]:
            return GuangSan(card_string, 2, get_order(card_string[0]))


class SanDaiYi(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) != 4:
            return None
        if card_string[0] == card_string[1] == card_string[2] != card_string[3]:
            return SanDaiYi(card_string, 3, get_order(card_string[0]))
        elif card_string[0] != card_string[1] == card_string[2] == card_string[3]:
            return SanDaiYi(card_string, 3, get_order(card_string[1]))


class SanDaiEr(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) != 5:
            return None
        if card_string[0] == card_string[1] == card_string[2] != card_string[3] == card_string[4]:
            return SanDaiYi(card_string, 4, get_order(card_string[0]))
        elif card_string[0] == card_string[1] != card_string[2] == card_string[3] == card_string[4]:
            return SanDaiYi(card_string, 4, get_order(card_string[2]))


class ShunZi(CardType):
    def __init__(self, display, length, order):
        CardType.__init__(self, display, 5, order)
        self.length = length

    @staticmethod
    def parse(card_string):
        if len(card_string) < 5:
            return None

        test_shunzi = is_shunzi(card_string)
        if test_shunzi is not None:
            return ShunZi(card_string, len(card_string), test_shunzi)

    def display_logic(self):
        return '{}: type_no = {} length = {} order = {}'.format(self.__class__.__name__, self.type_no, self.length, self.order)


class JieMeiDui(CardType):
    def __init__(self, display, length, order):
        CardType.__init__(self, display, 6, order)
        self.length = length

    @staticmethod
    def parse(card_string):
        if len(card_string) < 6 or len(card_string) % 2 != 0:
            return None

        if card_string[::2] == card_string[1::2]:
            test_shunzi = is_shunzi(card_string[::2])
            if test_shunzi is not None:
                return JieMeiDui(card_string, len(card_string) // 2, test_shunzi)

    def display_logic(self):
        return '{}: type_no = {} length = {} order = {}'.format(self.__class__.__name__, self.type_no, self.length, self.order)


class GuangFei(CardType):
    def __init__(self, display, length, order):
        CardType.__init__(self, display, 7, order)
        self.length = length

    @staticmethod
    def parse(card_string):
        if len(card_string) < 6 or len(card_string) % 3 != 0:
            return None

        if card_string[::3] == card_string[1::3] == card_string[2::3]:
            test_shunzi = is_shunzi(card_string[::3])
            if test_shunzi is not None:
                return GuangFei(card_string, len(card_string) // 3, test_shunzi)

    def display_logic(self):
        return '{}: type_no = {} length = {} order = {}'.format(self.__class__.__name__, self.type_no, self.length, self.order)


class FeiJi(CardType):
    def __init__(self, display, length, order):
        CardType.__init__(self, display, 8, order)
        self.length = length

    @staticmethod
    def parse(card_string):
        if len(card_string) < 10 or len(card_string) % 5 != 0:
            return None

        temp = card_string
        sanzhang = ''.join([temp[index] for index in range(len(temp) - 2) if temp[index] == temp[index+1] == temp[index+2]])
        for ch in sanzhang:
            temp = temp.replace(ch, '')
        erzhang = ''.join([temp[index] for index in range(len(temp) - 1) if temp[index] == temp[index+1]])

        if len(sanzhang) != len(erzhang):
            return None
        if is_shunzi(erzhang) is None:
            return None
        test_feiji = is_shunzi(sanzhang)
        if test_feiji is not None:
            return FeiJi(card_string, len(sanzhang), test_feiji)

    def display_logic(self):
        return '{}: type_no = {} length = {} order = {}'.format(self.__class__.__name__, self.type_no, self.length, self.order)


class SiDaiEr(CardType):
    @staticmethod
    def parse(card_string):
        if len(card_string) != 6:
            return None

        sizhang = [card_string[index] for index in range(len(card_string) - 3) if card_string[index] == card_string[index+1] == card_string[index+2] == card_string[index+3]]
        if len(sizhang) == 1:
            return SiDaiEr(card_string, 9, get_order(sizhang[0]))



class ZhaDan(CardType):
    def __init__(self, display, mag, order):
        CardType.__init__(self, display, 10, order)
        self.mag = mag

    @staticmethod
    def parse(card_string):
        if card_string == 'SB':
            return ZhaDan('SB', 100, 0)

        if len(card_string) < 4:
            return None

        if card_string.replace(card_string[0], '') == '':
            return ZhaDan(card_string, len(card_string), get_order(card_string[0]))

    def display_logic(self):
        return '{}: type_no = {} mag = {} order = {}'.format(self.__class__.__name__, self.type_no, self.mag, self.order)

class Dummy(CardType): pass

type_class = [DanZhang, DuiZi, GuangSan, SanDaiYi, SanDaiEr, ShunZi, JieMeiDui, GuangFei, FeiJi, SiDaiEr, ZhaDan]

DUMMY_TYPE = Dummy('None', -1, -1)
