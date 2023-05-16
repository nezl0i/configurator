import re
import sys
import json
from typing import List
from common import meters
from common.colors import c
from datetime import datetime
from decorators.status import is_status
from common import execute, hardware, parse_event
from core.abstract_protocol import AbstractIncotexProtocol
from common.check_response import check_response, check_out


class IncotexProtocol(AbstractIncotexProtocol):

    def test_channel(self, command: List[str]) -> None:
        """Тест канала связи """
        out = self.exchange(command, 4)[1]
        check_response(self.test_channel.__doc__, out)

    def open_session(self, command: List[str]) -> None:
        """Авторизация с устройством """
        out = self.exchange(command, 4)[1]
        if out[0]:
            self.status = True
        check_response(self.open_session.__doc__, out)

    @is_status
    def close_session(self, command: List[str]) -> None:
        """Закрытие сеанса с устройством """
        out = self.exchange(command, 4)[1]
        if out[0]:
            self.status = False
        check_response(self.close_session.__doc__, out)

    @is_status
    def get_identifier(self, command: List[str]) -> str:
        """Идентификатор ПУ """
        out = self.exchange(command, 5)[1]
        result = int(out[2], 16)
        print(f'{c.GREEN}{self.get_identifier.__doc__} - {result}{c.END}\n')
        return out[2]

    @is_status
    def get_serial_number(self, command: List[str]) -> tuple:
        """Чтение серийного номера и даты выпуска """
        out = self.exchange(command, 10)[1]
        tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), out))
        serial_number = ''.join(tmp_check_out[1:5])
        work_data = '.'.join(tmp_check_out[5:8])
        print(f'{c.GREEN}Серийный номер - {serial_number}\n'
              f'Дата выпуска - {work_data}{c.END}\n')
        return serial_number, work_data

    @staticmethod
    def to_bit(item: str) -> str:
        return format(int(item, 16), "08b")

    @staticmethod
    def to_list(item: str) -> list:
        return list(map(lambda x: str(int(x, 16)).zfill(2), item))

    @is_status
    def get_execution(self, command: List[str]):
        """Чтение варианта исполнения """
        var = self.exchange(command, 27)[1]
        tmp_serial = self.to_list(var[1:5])
        tmp_data = self.to_list(var[5:8])
        tmp_version = self.to_list(var[8:11])
        tmp_revision = self.to_list(var[19:21])
        device_serial_number = ''.join(tmp_serial)
        data = '.'.join(tmp_data)
        version = '.'.join(tmp_version)
        revision = '.'.join(tmp_revision)
        crc_po = f"{''.join(var[17:19]).upper()}"

        byte_1 = self.to_bit(var[11])
        byte_2 = self.to_bit(var[12])
        byte_3 = self.to_bit(var[13])
        byte_4 = self.to_bit(var[14])
        byte_5 = self.to_bit(var[15])
        byte_6 = self.to_bit(var[16])
        byte_7 = self.to_bit(var[21])
        # byte_8 = format(int(check_out[22], 16), "08b")
        make_revision = execute.get_revision((byte_3[4:]))
        device_impulse = execute.byte_25(byte_2[4:]).split()[0]
        execute.print_exec(device_serial_number, data, version, revision, crc_po, byte_1, byte_2,
                           byte_3, byte_4, byte_5, byte_6, byte_7)

        return version, make_revision, crc_po, device_impulse

    @is_status
    def get_descriptor(self, command: List[str]) -> None:
        """Чтение дескриптора и типа микроконтроллера """
        out = self.exchange(command, 5)[1]
        desc = f'{out[2]}{out[1]}'
        print(f'{c.GREEN}Дескриптор ПУ - {desc}\n'
              f'Микроконтроллер - {hardware.HARDWARE[desc.upper()]}{c.END}\n')

    @is_status
    def get_vectors(self, command: List[str]) -> None:
        """Вектора прерываний """
        var = []
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            var.append(' '.join(self.exchange(command, 19, param=param[i])[1][1:16]))
        print(f'{c.GREEN}{self.get_vectors.__doc__}:')
        print(*var, c.END, sep='\n')

    def get_password(self, command: List[str]) -> None:
        """Чтение паролей """
        var = []
        param = ['00 4F 06', '00 48 06']
        for i in range(len(param)):
            var.append(self.exchange(command, 9, param=param[i])[1][1:7])
        for i, el in enumerate(var, 1):
            passwd = ''.join(map(lambda x: str(int(x, 16)), el))
            if len(passwd) == 6:
                print(f'{c.GREEN}Пароль {i} уровня- {passwd} (HEX){c.END}')
            else:
                passwd = ''.join(map(lambda x: bytearray.fromhex(x).decode(), el))
                print(f"{c.GREEN}Пароль {i} уровня- {''.join(passwd)} (ASCII){c.END}")
        print('\n')

    @is_status
    def set_passwd(self, command: List[str], current_password: str, current_level: int) -> None:
        """Запись паролей для текущего уровня доступа """
        pwd = input('Введите пароль: _ ')
        pass_mode = input('Кодировка (hex/ascii): ')
        if pass_mode == 'hex':
            tmp_pass = ' '.join((format(int(i), '02X')) for i in pwd)
        elif pass_mode == 'ascii':
            tmp_pass = ' '.join((format(ord(i), '02X')) for i in pwd)
        else:
            print('Bad password mode (use "hex" or "ascii").')
            sys.exit()
        out = self.exchange(command, 4, param=f'{current_level} {current_password} {tmp_pass}')[1]
        check_response('Изменение пароля', out)

    @is_status
    def get_shunt(self, command: List[str], version: str) -> None:
        """Чтение параметров программного шунта """
        # version  = "2" - Меркурий-230
        # version  = "3" - Меркурий-231
        # version  = "4" - Меркурий-232
        # version  = "7"  - Меркурий-233
        # version  = "8" - Меркурий-236
        # version  = "9" - Меркурий-234
        # version  = "11" - Меркурий-231i

        param = None

        match int(version.split('.')[0], 16):
            case 9:
                param = '19 00 0A'
            case 2 | 8:
                param = '10 70 0A'
            case 11:
                param = '10 00 0A'
            case _:
                print('Тип прибора не определен.')

        out = self.exchange(command, 13, param=param)[1]
        shunt_mode = int(out[3], 16)
        event_code = int(out[4], 16)

        print_event_code = 'отключен' if event_code == 1 else 'не отключен'

        match shunt_mode:
            case 1:
                shunt_value = int(out[1], 16)
                percent = 100 - (100 / shunt_value)
            case 2:
                shunt_value = int(out[2], 16) + 1
                percent = 100 / shunt_value
            case _:
                shunt_mode = 'не определено'
                shunt_value = 'не определено'
                percent = 0

        print(f'{c.GREEN}Текущий режим - {shunt_mode}{c.END}')
        print(f'{c.GREEN}Значение - {shunt_value}{c.END}')
        print(f'{c.GREEN}Недоучет - {percent} %{c.END}')
        print(f'{c.GREEN}Журнал "Дата и код программирования" - {print_event_code}{c.END}\n')

    @is_status
    def write_shunt(self, command: List[str], code=True) -> None:

        percent = int(input('Процент недоучета: '))
        w_code = '01' if code else '00'

        if percent > 50:
            value = format(int(100 / (100 - percent)), "02X")
            param = f'{value} 00 01 {w_code} 00 00 00 00 00 00'
        elif percent == 0:
            param = f'00 00 00 {w_code} 00 00 00 00 00 00'
        else:
            value = format(int(100 / percent), "02X")
            param = f'00 {value} 02 {w_code} 00 00 00 00 00 00'
        out = self.exchange(command, 4, param=param)[1]
        check_response('Команда записи шунта', out)

    @is_status
    def get_time(self, command: List[str]) -> None:
        week_day = {'01': 'Понедельник', '02': 'Вторник', '03': 'Среда',
                    '04': 'Четверг', '05': 'Пятница', '06': 'Суббота', '07': 'Воскресение'}
        device_time = self.exchange(command, 11)[1][1:9]
        print(f'\nВремя прибора: {".".join(list(device_time[4:7]))}'
              f' {":".join(list(device_time[:3])[::-1])}'
              f' {week_day[device_time[3]]}'
              f' {"Зима" if device_time[7] == "01" else "Лето"}\n')

    @staticmethod
    def fill(*args) -> str:
        return str(args[0]).zfill(2)

    @is_status
    def set_time(self, command: List[str]) -> None:
        """Установка даты и времени"""

        month = [1, 2, 3, 10, 11, 12]
        dt = datetime.now()
        seconds = self.fill(dt.second)
        minutes = self.fill(dt.minute)
        hours = self.fill(dt.hour)
        weeks = self.fill(dt.weekday() + 1)
        days = self.fill(dt.day)
        months = self.fill(dt.month)
        years = str(dt.year)[-2:]
        seasons = self.fill(1 if dt.month in month else 0)
        param = f'{seconds} {minutes} {hours} {weeks} {days} {months} {years} {seasons}'
        out = self.exchange(command, 4, param=param)[1]
        check_response(self.set_time.__doc__, out)
        # self.time_get()

    @is_status
    def clear_meters(self, command: List[str]) -> None:
        """ Сброс регистров накопленной энергии"""
        out = self.exchange(command, 4)[1]
        check_response(self.clear_meters.__doc__, out)

    @staticmethod
    def two_split(tmp_str: str) -> str:
        b = re.findall(r'\d\d', tmp_str)
        return " ".join(map(lambda x: format(int(x), '02X'), b))

    @staticmethod
    def date_split(tmp_str: str) -> str:
        b = tmp_str.split(".")
        return " ".join(map(lambda x: format(int(x), '02X'), b))

    @is_status
    def write_serial_and_date(self, command: List[str]) -> None:
        """ Запись серийного номера и даты выпуска"""
        serial = input('Серийный номер: ')
        date = input('Дата выпуска (дд.мм.гг): ')
        send_serial = self.two_split(serial)
        send_date = self.date_split(date)
        param = f'{send_serial} {send_date} 00'
        out = self.exchange(command, 4, param=param)[1]
        check_response(self.write_serial_and_date.__doc__, out)

    @is_status
    def set_data(self, command: List[str]) -> None:
        """Прямая запись по физическим адресам памяти"""
        memory = format(int(input('Номер памяти: ')), '02X')
        offset = input('Адрес (через пробел "00 4f"): ')
        count = format(int(input('Количество байт: ')), '02X')
        data = input('Данные (через пробел): ')
        send_data = f'{memory} {offset} {count} {data}'
        out = self.exchange(command, 4, param=send_data)[1]
        check_response('Команда записи', out)

    @is_status
    def get_event(self, command: List[str]) -> None:
        """Чтение журналов событий"""

        number = int(input('Номер журнала (1-26), 0 - все журналы: _ '))
        position = int(input('Номер записи (1-10), 0 - все записи: _ '))

        if not isinstance(number, int) or not isinstance(position, int):
            print('Не верно указаны параметры.')
            sys.exit()

        list_all = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B', '0C', '0D',
                    '0E', '0F', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A']

        list_0 = ['07', '08', '09', '0A', '0B', '0C', '0D', '0E', '0F', '10', '11', '15', '16']
        param = None
        pos = None
        tmp_key = []
        tmp_out = []
        tmp_event = []
        flag = 1

        if number and not position:
            if number <= 26:
                param = format(number, '02X')
                flag = 3
            else:
                print('Некорректный номер журнала')
                sys.exit()

        elif number and position:
            if number <= 26 and position <= 10:
                position -= 1
                param = format(number, '02X')
                pos = format(position, '02X')
                flag = 4
            else:
                print('Некорректный введен номер параметра')
                sys.exit()
        elif not number and position:
            if position <= 10:
                position -= 1
                pos = format(position, '02X')
                flag = 2

        for i in range(len(list_all)):
            key = list_all[i]
            tmp_out.clear()
            count = 9 if list_all[i] in list_0 else 15

            if flag == 1:
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(self.exchange(command, count, param=f'{key} {index}')[1])
            elif flag == 2:
                tmp_out.append(self.exchange(command, count, param=f'{key} {pos}')[1])
            elif flag == 3:
                count = 9 if param in list_0 else 15
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(list(self.exchange(command, count, param=f'{param} {index}')[1]))
                tmp_event.append(tmp_out[:])
                tmp_key.append(param)
                break
            elif flag == 4:
                count = 9 if param in list_0 else 15
                tmp_out.append(list(self.exchange(command, count, param=f'{param} {pos}')[1]))
                tmp_event.append(tmp_out[:])
                tmp_key.append(key)
                break
            tmp_event.append(tmp_out[:])
            tmp_key.append(key)

        event_dict = dict(zip(tmp_key, tmp_event))
        return parse_event.print_log(event_dict)

    @is_status
    def clear_event(self, command: List[str], file: str) -> None:

        journal = input('Номер журнала (1-26), 0 - все журналы: _ ')
        number = input('Номер записи (1-10), 0 - все записи: _ ')

        clear_event = json.load(open(file, encoding="utf-8"))

        if int(journal) and not int(number):
            for key, value in clear_event[journal].items():
                param = ' '.join(value)
                out = self.exchange(command, 4, param=param)[1]
                check_response(f'Очистка журнала [{journal}], запись [{key}]', out)
        elif int(journal) and int(number):
            param = ' '.join(clear_event[journal][number])
            out = self.exchange(command, 4, param=param)[1]
            check_response(f'Очистка журнала [{journal}], запись [{number}]', out)
        elif not int(journal) and not int(number):
            for key in clear_event.keys():
                for key2, value in clear_event[key].items():
                    param = ' '.join(value)
                    out = self.exchange(command, 4, param=param)[1]
                    check_response(f'Очистка журнала [{key}], запись [{key2}]', out)
        else:
            print('Не самый лучший вариант. Попробуй другие параметры.')

    @is_status
    def update_firmware(self, command: List[str], file: str) -> None:
        hi_address = None
        lo_address = None
        arg_value = None

        with open(file, encoding='utf8') as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('@'):
                arg_value = '02'
                hex_line = line[1:].rstrip()

                if hex_line[0].isdigit():
                    hi_address = format(int(hex_line[:2], 16), "02X")
                    lo_address = format(int(hex_line[2:4], 16), "02X")
                else:
                    hi_address = format(int(hex_line[0], 16), "02X")
                    lo_address = format(int(hex_line[1:3], 16), "02X")

            elif line.startswith('q'):
                send_command = '12 0F 3C 0F FC 10'
                out = self.exchange(command, 4, param=send_command)[1]
                if out[1] == '00':
                    print(f'{c.GREEN}Обновление выполнено успешно!{c.END}')
                else:
                    print(f'{c.FAIL}Не удалось выполнить обновление...{c.END}')
                return
            else:
                send_command = f'{arg_value} {hi_address} {lo_address} {line.rstrip()}'
                self.exchange(command, 4, param=send_command)
                if lo_address == 'FF':
                    hi_address = format(int(hi_address, 16) + 1, "02X")
                    lo_address = '00'
                    arg_value = '00'
                else:
                    lo_address = format(int(lo_address, 16) + 1, "02X")
                    arg_value = '00'

    def _param_select(self, command: List[str], param: List[str]) -> None:
        """Запись показаний"""
        for i in range(len(param)):
            out = self.exchange(command, 4, param=param[i])[1]
            check_response(self._param_select.__doc__, out)

    @is_status
    def write_meters(self, command: List[str], file: str, make_revision: str) -> None:
        meter = json.load(open(file, encoding='utf8'))
        k = 1
        match make_revision:
            case '00':
                k = 10
            case '01':
                k = 1
            case '02':
                k = 2
            case '03':
                k = 2

        keys = ("A+", "PhaseA", "Year_A+", "Year_old_A+", "January_A+", "February_A+", "March_A+", "April_A+",
                "May_A+", "June_A+", "July_A+", "August_A+", "September_A+", "October_A+", "November_A+",
                "December_A+", "Day_A+", "Day_old_A+")

        make_define = (meters.EnergyReset, meters.EnergyPhase, meters.EnergyYear, meters.EnergyOldYear,
                       meters.EnergyJanuary, meters.EnergyFebruary, meters.EnergyMarch, meters.EnergyApril,
                       meters.EnergyMay, meters.EnergyJune, meters.EnergyJuly, meters.EnergyAugust,
                       meters.EnergySeptember, meters.EnergyOctober, meters.EnergyNovember, meters.EnergyDecember,
                       meters.EnergyDay, meters.EnergyOldDay)

        joined_make = list(zip(keys, make_define))

        for key in joined_make:
            if key[0] in meter:
                self._param_select(command, key[1](k))

    @is_status
    def set_spodes(self, command: List[str]) -> None:
        """Переключение протоколов"""
        interface = {0: "Оптопорт", 1: "Встроенный", 2: "Левый канал", 3: "Правый канал"}
        default_protocol = {0: "Меркурий", 1: "СПОДЭС"}
        try:
            channel = int(input('Канал 0 – оптопорт, 1 – встроенный, 2 – левый, 3 – правый: '))
        except ValueError:
            print('Не выбран канал связи')
            sys.exit()
        try:
            value = int(input('Протокол 0 – «Меркурий», 1 – «СПОДЭС»: '))
        except ValueError:
            print('Не выбран протокол')
            sys.exit()
        ch = format(channel, '02X')
        val = format(value, '02X')
        try:
            byte_timeout = int(input('межсимвольный таймаут (default 300): '))
        except ValueError:
            byte_timeout = 300
        try:
            active_time = int(input('Таймаут не активности (default 120): '))
        except ValueError:
            active_time = 120

        lo_byte_timeout = format(byte_timeout, '04X')[:2]
        hi_byte_timeout = format(byte_timeout, '04X')[2:]
        act_time = format(active_time, '02X')

        param = f'{ch} {val} 00 {hi_byte_timeout} {lo_byte_timeout} {act_time}'
        out = self.exchange(command, 4, param=param)[1]
        print(f'{c.GREEN}Интерфейс - "{interface[channel]}"\n'
              f'Протокол - "{default_protocol[value]}"\n'
              f'Межсимвольный таймаут - {byte_timeout}\n'
              f'Таймаут не активности - {active_time}\n'
              f'Выполнение - {check_out(out[1])}{c.END}\n')


protocol = IncotexProtocol()
