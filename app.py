import sys
from common.logo import c
from config import config as cfg
from core.protocol import protocol
from common.class_brut import Brutforce
from common.enum_command import ICommand
from common.menu import menu, event_menu
from core.build_device import director, device


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
            sys.exit()
    except (ValueError, KeyboardInterrupt, KeyError):
        main_menu()


def choice(tmp):
    match tmp:
        case 1:
            director.construct(device)
        case 2:
            event_menu()
            protocol.get_event(command.GET_EVENT)
        case 3:
            protocol.get_time(command.GET_TIME)
        case 4:
            protocol.set_data(command.SET_DATA)
        case 5:
            protocol.set_time(command.SET_TIME)
        case 6:
            protocol.get_shunt(command.GET_SHUNT, device.IA.DEVICE_VERSION)
        case 7:
            protocol.clear_meters(command.CLEAR_METERS)
        case 8:
            protocol.write_shunt(command.SET_SHUNT)
        case 9:
            protocol.get_descriptor(command.GET_DESCRIPTOR)
        case 10:
            protocol.write_meters(command.SET_METERS, device.IA.METERS_FILE, device.IA.DEVICE_REVISION)
        case 11:
            protocol.get_vectors(command.GET_VECTORS)
        case 12:
            protocol.update_firmware(command.UPDATE_FIRMWARE, device.IA.FIRMWARE_FILE)
        case 13:
            protocol.get_password(command.GET_PASSWD)
        case 14:
            protocol.write_serial_and_date(command.SET_SERIAL)
        case 15:
            protocol.set_passwd(command.SET_PASSWD, device.IA.DEVICE_LEVEL, device.IA.DEVICE_PASSWORD)
        case 16:
            event_menu()
            protocol.clear_event(command.SET_METERS, device.IA.CLEAR_EVENTS_FILE)
        case 17:
            protocol.set_spodes(command.SET_SPODES)
        case 18:
            Brutforce().brut_password()
        case 19:
            protocol.read_profile(command.LAST_PROFILE, device.IA.DEVICE_IMPULSE, device.IA.DEVICE_SERIAL_NUMBER)
        case 20:
            protocol.write_profile(command.LAST_PROFILE, device.IA.DEVICE_IMPULSE, cfg.SHEET_NAME)
        case 0:
            sys.exit()


if __name__ == '__main__':
    main_menu()
