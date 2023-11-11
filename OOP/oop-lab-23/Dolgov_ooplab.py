from colorama import Fore, Style
import re


#furnishing class
class Furnishing():
    def __init__(self, size: list, coords: list):
        self.size = size
        self.coords = coords
    
    def get_placing(item):
        size_1 = item.size 
        coords_1 = item.coords 

        placing = {"side_hor": [coords_1[0], coords_1[0] + size_1[0]], 
                   "side_vert": [coords_1[1], coords_1[1] + size_1[1]]}
        return placing
    
    def check_overlap(item_1, item_2):
        placing_1 = Furnishing.get_placing(item_1)
        placing_2 = Furnishing.get_placing(item_2)

        intersec = 0
        for hor in placing_2['side_hor']:
            if hor >= placing_1['side_hor'][0] and hor <= placing_1['side_hor'][1]:
                intersec += 1 
                break
        for vert in placing_2['side_vert']:   
            if vert >= placing_1['side_vert'][0] and vert <= placing_1['side_vert'][1]:
                intersec += 1 
                break
        if intersec == 2:
            return True
        else:
            return False


#cupboard class
class Cupboard(Furnishing):
    def __init__(self, material: str, size: list, coords: list):
        self.material = material
        self.size = size
        self.coords = coords

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)
    
    def check_overlap_diff_mat(item_1, item_2):
        placing_1 = Furnishing.get_placing(item_1)
        placing_2 = Furnishing.get_placing(item_2)
        
        if item_1.material == item_2.material:
            return None
        else:
            diffs = [abs(i) for i in [placing_1["side_hor"][0] - placing_2["side_hor"][1],
                                      placing_1["side_hor"][1] - placing_2["side_hor"][0],
                                      placing_1["side_vert"][0] - placing_2["side_vert"][1],
                                      placing_1["side_vert"][1] - placing_2["side_vert"][0]]]
            
            if (diffs[0] or diffs[1]) < 2 and (diffs[2] or diffs[3]) < 2:
                    return True
            else:
                return False


#kappliance class
class KAppliance(Furnishing):
    def __init__(self, name: str, size: list, coords: list, power = False):
        self.name = name
        self.size = size
        self.coords = coords
        self.power = power

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)

    def kappliance_on_ground(kapp_1): 
        coords_1 = kapp_1.coords
        if coords_1[2] > 0:
            return False
        else:
            return True

    def toggle(kapp_1):
        state = ""
        if kapp_1.power is False:
            kapp_1.power = True 
            state = "ON"
        else:
            kapp_1.power = False
            state = "OFF"
        return Fore.CYAN + f"{kapp_1.name.capitalize()} is {state}" + Style.RESET_ALL


#kitchen plan class
class KitchenPlan():
    def __init__(self, kitchen_size: list, items: list):
        self.kitchen_size = kitchen_size 
        self.items = items

    def general_check(kitchen_size: list, items: list):
        err_count = 0
        kitchen_coords = {"side_x": [0, kitchen_size[0]], 
                          "side_y": [0, kitchen_size[1]]}
        
        #sort class objects
        cupboards_list = []
        kappliance_list = []
        for item in items:
            if isinstance(item, Cupboard):
                cupboards_list.append(item)
            elif isinstance(item, KAppliance):
                kappliance_list.append(item)

        #check fitting in kitchen
        local_errs = 0
        for item in items:
            item_placing = Furnishing.get_placing(item)
            collisions = 0
            for i in item_placing["side_hor"]:
                if i < kitchen_coords["side_x"][0] or i > kitchen_coords["side_x"][1]:
                    collisions += 1 
                    break
            for j in item_placing["side_vert"]:   
                if j < kitchen_coords["side_y"][0] or i > kitchen_coords["side_y"][1]:
                    collisions += 1 
                    break
            if collisions >= 1:
                if isinstance(item, Cupboard):
                    print(Fore.RED + f"ВНИМАНИЕ: Шкаф находится вне кухни. Попробуйте увеличить размер кухни или переместить шкаф." + Style.RESET_ALL)
                elif isinstance(item, KAppliance):
                    print(Fore.RED + f"ВНИМАНИЕ: Бытовая техника находится вне кухни. Попробуйте увеличить размер кухни или переместить технику." + Style.RESET_ALL)              
                err_count += 1
                local_errs += 1
        if local_errs == 0:
            print(Fore.GREEN + "Все элементы кухонного гарнитура находятся в кухне!" + Style.RESET_ALL)

        #check overlap - cb and kapp
        local_errs = 0
        for cupboard in cupboards_list:
            for kapp in kappliance_list:
                if Furnishing.check_overlap(cupboard, kapp) is True:
                    print(Fore.RED + f"ВНИМАНИЕ: {kapp.name[0].capitalize()} пересекается со шкафом. Попробуйте переместить технику или шкаф." + Style.RESET_ALL)
                    err_count += 1
                    local_errs += 1
        
        #check overlap - cb and cb
        dup_cupboards_list = cupboards_list
        for cb in cupboards_list:
            for dcb in dup_cupboards_list:
                if cb != dcb:
                    if Furnishing.check_overlap(cb, dcb) is True:
                        print(Fore.RED + "ВНИМАНИЕ: Шкафы пересекаются. Попробуйте переместить один из них." + Style.RESET_ALL)
                        err_count += 1
                        local_errs += 1

        #check overlap - kapp and kapp
        dup_kappliance_list = kappliance_list
        for kapp in kappliance_list:
            for dkapp in dup_kappliance_list:
                if kapp != dkapp:
                    if Furnishing.check_overlap(kapp, dkapp) is True:
                        print(Fore.RED + "ВНИМАНИЕ: Бытовая техника пересекается. Попробуйте переместить одну из них." + Style.RESET_ALL)
                        err_count += 1
                        local_errs += 1
    
        if local_errs == 0:
            print(Fore.GREEN + "Элементы кухонного гарнитура не пересекаются друг с другом!" + Style.RESET_ALL)

        #check distance - cb of different materials
        local_errs = 0
        dup_cupboards_list = cupboards_list
        for cb in cupboards_list:
            for dcb in dup_cupboards_list:
                if cb != dcb:
                    if Cupboard.check_overlap_diff_mat(cb, dcb) is True:
                        print(Fore.RED + "ВНИМАНИЕ: Шкафы из разного материала находятся ближе 2-х метров друг к другу. Попробуйте переместить один из них." + Style.RESET_ALL)
                        err_count += 1
                        local_errs += 1
        if local_errs == 0:
            print(Fore.GREEN + "Шкафы из разного материала находятся не ближе 2-х метров друг к другу!" + Style.RESET_ALL)


        #check kapp floating
        local_errs = 0
        for kapp in kappliance_list:
            if KAppliance.kappliance_on_ground(kapp) is False:
                print(Fore.RED + "ВНИМАНИЕ: Бытовая техника находится в воздухе. Попробуйте поставить ее на пол." + Style.RESET_ALL)
                err_count += 1
                local_errs += 1
        if local_errs == 0:
            print(Fore.GREEN + "Вся бытовая техника находится на полу!" + Style.RESET_ALL)
        

        if err_count == 0:
            return (Fore.MAGENTA + "\nПроверка выполнена успешно - все требования к планировке кухни удовлетворены!" + Style.RESET_ALL).center(50)
        else:
            return (Fore.RED + "\nВыполните все требования к планировке кухни, указанные выше." + Style.RESET_ALL).center(50)

#interaction / inputs:
print((f"{Fore.BLUE}\nДобро пожаловать в приложение планировки кухни!\n\n").center(50), (f"Следуйте указаниям, указанным ниже:\n\n\n{Style.RESET_ALL}").center(50))

raw_kitchen_size = input(f"Впишите размер кухни в метрах в формате [x, y]: \n\n{Fore.YELLOW}Пример оформления: \n[20.5, 35]: {Style.RESET_ALL}\n\n")
kitchen_coords = re.findall(r"\[.*?\]", raw_kitchen_size)
strkitchen_coords = kitchen_coords[0][1:-1].split(",")
kitchen_size = [float(num) for num in strkitchen_coords]

kitchen_items = []
print(f'\n\n\nПри вводе характеристик элементов кухонного гарнитура (шкафов, бытовой техники), помните: \n1. Мебель и техника не должны пересекаться \n2. Техника не должна находиться в воздухе \n3. Мебель из разных материалов должна быть расположена на расстоянии не меньше 2 метров друг от друга\n')
while True:
    choice = input(f'\n{Fore.RED}(Если ввод элементов закончен, впишите "стоп"){Style.RESET_ALL} \nВведите желаемый элемент кухонного гарнитура (ш - шкаф, бт - бытовая техника): ')
    if "стоп" in choice:
            break
    
    elif "ш" in choice:
        raw_cb_item = input(f'{Fore.YELLOW}\n\nШаблон оформления характеристик шкафа: \n"дуб", [2, 0.5, 3], [3, 2, 0]{Style.RESET_ALL}\nВпишите характеристики шкафа: ')

        material = re.findall(r'\"(.*?)\"', raw_cb_item)
        sizecoords_cb = re.findall(r"\[.*?\]", raw_cb_item)
        strsize_cb = sizecoords_cb[0][1:-1].split(",")
        size_cb = [float(num) for num in strsize_cb]
        strcoords_cb = sizecoords_cb[1][1:-1].split(",")
        coords_cb = [float(num) for num in strcoords_cb]
    
        cupboard = Cupboard(material, size_cb, coords_cb)
        kitchen_items.append(cupboard)

    elif "бт" in choice:
        raw_kapp_item = input(f'{Fore.YELLOW}\n\nШаблон оформления характеристик бытовой техники: \n"микроволновка", [0.3, 0.2, 2], [5, 2, 0]{Style.RESET_ALL}\nВпишите характеристики бытовой техники: ')
    
        name = re.findall(r'\"(.*?)\"', raw_kapp_item)
        sizecoords_ka = re.findall(r"\[.*?\]", raw_kapp_item)
        strsize_ka = sizecoords_ka[0][1:-1].split(",")
        size_ka = [float(num) for num in strsize_ka]
        strcoords_ka = sizecoords_ka[1][1:-1].split(",")
        coords_ka = [float(num) for num in strcoords_ka]
        
        kapp = KAppliance(name, size_ka, coords_ka)
        kitchen_items.append(kapp)

    else:
        print(f'\n{Fore.RED}Выберите один из указанных элементов кухонного гарнитура, либо впишите "стоп" для завершения ввода!{Style.RESET_ALL}')

if kitchen_items == [] or kitchen_size == []:
    print(f"{Fore.RED}\nВНИМАНИЕ: Пожалуйста, введите действительные значения для размера кухни и характеристик элементов\n\n{Style.RESET_ALL}")
else:
    print(f"\n\n\n{Fore.BLUE}Введенные элементы кухонного гарнитура:{Style.RESET_ALL}\n")

    for item in kitchen_items:
        if isinstance(item, Cupboard):
            print(f"Шкаф, материал: {item.material}, размер: {item.size}, координаты: {item.coords}")
        elif isinstance(item, KAppliance):
            print(f"Бытовая техника, наименование: {item.name}, размер: {item.size}, координаты: {item.coords}")
    print(f"{Fore.BLUE}\nВвод элементов кухонного гарнитура окончен, результат проверки:\n\n{Style.RESET_ALL}")

    print(KitchenPlan.general_check(kitchen_size, kitchen_items))