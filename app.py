import sys
from core.protocol import protocol
from core.build_device import director, device
from common.enum_command import ICommand
from common.logo import c
from common.menu import menu, event_menu
from common import class_brut

command = ICommand()


def main_menu():
    menu()

    try:
        ans = int(input(f'{c.GREEN}Enter a choice: ~# {c.END}'))
        choice(ans)
        ready = input('Продолжить? (y/n): ')
        to_answer = ('y', 'yes', 'д', 'да')
        if ready in to_answer:
            main_menu()
        else:
            print(f'{c.FAIL}Не верно указан параметр{c.END}\n')
            sys.exit()
    except ValueError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError:
        main_menu()


def choice(tmp):
    match tmp:
        case 1:
            director.construct(device)
        case 2:
            protocol.get_time(command.GET_TIME)
        case 3:
            protocol.set_time(command.SET_TIME)
        case 4:
            protocol.clear_meters(command.CLEAR_METERS)
        case 5:
            protocol.get_descriptor(command.GET_DESCRIPTOR)
        case 6:
            protocol.get_vectors(command.GET_VECTORS)
        case 7:
            protocol.get_password(command.GET_PASSWD)
        case 8:
            protocol.set_passwd(command.SET_PASSWD, device.IA.DEVICE_LEVEL, device.IA.DEVICE_PASSWORD)
        case 9:
            protocol.set_spodes(command.SET_SPODES)
        case 10:
            event_menu()
            protocol.get_event(command.GET_EVENT)
        case 11:
            protocol.set_data(command.SET_DATA)
        case 12:
            protocol.get_shunt(command.GET_SHUNT, device.IA.DEVICE_VERSION)
        case 13:
            protocol.write_shunt(command.SET_SHUNT)
        case 14:
            protocol.write_meters(command.SET_METERS, device.IA.METERS_FILE, device.IA.DEVICE_REVISION)
        case 15:
            protocol.update_firmware(command.UPDATE_FIRMWARE, device.IA.FIRMWARE_FILE)
        case 16:
            protocol.write_serial_and_date(command.SET_SERIAL)
        case 17:
            event_menu()
            protocol.clear_event(command.SET_METERS, device.IA.CLEAR_EVENTS_FILE)
        case 18:
            # protocol.close_session(command.CLOSE_SESSION)
            class_brut.Brutforce().brut_password()
        case 0:
            sys.exit()


if __name__ == '__main__':
    main_menu()
