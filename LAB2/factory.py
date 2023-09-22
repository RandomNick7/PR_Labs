from player import Player
import xmltodict
from dicttoxml import dicttoxml
from pprint import pprint as pp
import json
import player_pb2

# Solutions used are specific to the structure of the Player object

class PlayerFactory:
    def to_json(self, players):
        # This function should transform a list of Player objects into a list with dictionaries.
        out_list = []
        for pl in players:
            temp_dict = vars(pl)
            temp_dict['class'] = temp_dict['cls']
            del temp_dict['cls']
            temp_dict['date_of_birth'] = temp_dict['date_of_birth'].strftime("%Y-%m-%d")
            out_list.append(temp_dict)
        return out_list

    def from_json(self, list_of_dict):
        # This function should transform a list of dictionaries into a list with Player objects.
        out_list = []
        for li in list_of_dict:
            val_arr = []
            for val in li.values():
                val_arr.append(val)
            out_list.append(Player(val_arr[0],val_arr[1],val_arr[2],val_arr[3],val_arr[4]))
        return out_list

    def from_xml(self, xml_string):
        # This function should transform a XML string into a list with Player objects.
        root = xmltodict.parse(xml_string)['data']['player']
        list_arr = []

        if(type(root) is dict):
            list_arr.append(root)
        else:
            list_arr = root

        out_list = []
        for val in list_arr:
            v_arr = []
            for v in val.values():
                v_arr.append(v)
            out_list.append(Player(v_arr[0],v_arr[1],v_arr[2],int(v_arr[3]),v_arr[4]))

        return out_list

    def to_xml(self, list_of_players):
        # This function should transform a list with Player objects into a XML string.
        out_str = ""
        for pl in list_of_players:
            str = dicttoxml(pl.__dict__, custom_root='player', xml_declaration=False, attr_type=False).decode("utf-8")
            str = str.replace('cls','class')
            str = str.replace('T00:00:00','')
            out_str += str
        out_str = '<data>'+out_str+"</data>"
        return out_str

    def from_protobuf(self, binary):
        # This function should transform a binary protobuf string into a list with Player objects.
        pb_pl = player_pb2.PlayersList()
        pb_pl.ParseFromString(binary)
        
        out_list = []
        for pl in pb_pl.player:
            out_list.append(Player(pl.nickname, pl.email, pl.date_of_birth.replace(' 00:00:00',''), pl.xp, pl.cls))
        return out_list

    def to_protobuf(self, list_of_players):
        # This function should transform a list with Player objects into a binary protobuf string.
        def add_player(p):
            p.nickname = pl.nickname
            p.email = pl.email
            p.date_of_birth = str(pl.date_of_birth)
            p.xp = pl.xp
            p.cls = pl.cls
    
        pb_pl = player_pb2.PlayersList()
        for pl in list_of_players:
            add_player(pb_pl.player.add())
        return pb_pl.SerializeToString()


# Small test to check if all works
'''
test = PlayerFactory()

player_arr = [Player("Alpha","alpha@gmail.com","2000-04-04",455,"Berserk"), Player("Beta","beta@gmail.com","2001-06-10",657,"Tank")]
byte_str = b'\n2\n\x05Alpha\x12\x0falpha@gmail.com\x1a\x132000-04-04 00:00:00 \xc7\x03(\x00\n0\n\x04Beta\x12\x0ebeta@gmail.com\x1a\x132001-06-10 00:00:00 \x91\x05(\x01'

print(test.from_protobuf(byte_str))
print(test.to_protobuf(player_arr))
'''