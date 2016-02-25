import os
import weakref


class StrWithExplicit(str):

    # def __init__(self, object):
    #     super().__init__(object)
    #     self.explicit = ""

    @property
    def int(self):
        return int(self or "0")


class ImplicitConfig:

    def __init__(self, config, settings):
        self._values = {}
        self._config = config
        self._settings = settings

        # self.__setattr__ = self.__setattr__function

    def get(self, key, default=""):
        value = self._values.get(key, default)
        explicit = self._config[key]
        # print(explicit)
        if not explicit:
            explicit = self._settings[key]
        if value:
            result = StrWithExplicit(value)
        else:
            result = StrWithExplicit(explicit)
        result.explicit = explicit
        return result

    def __getitem__(self, item):
        result = self.get(item)
        # print("get", item, repr(result))
        return result

    def __setitem__(self, key, value):
        # print("setitem", key, value)
        if not value:
            value = ""
        else:
            value = str(value)
        self._values[key] = value

    def __getattr__(self, item):
        result = self.get(item)
        # print("get", item, repr(result))
        return result
        # print("getattr", item)
        # if item == "_values":
        #     return getattr(self, "_values")
        # return self.get(item)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
        else:
            self[key] = value


class NoParent:

    def __call__(self):
        return None

    # def __nonzero__(self):
    #     return False


class Item:

    def __init__(self, text, active=True):
        self.text = text
        self.extra = ""
        # self.parent = parent
        self._active = active
        self.represents = []
        self.parent = NoParent()
        self.children = []

    # def set_parent(self, item):
    #     self.parent = item

    @property
    def active(self):
        return self._active

    def add(self, child):
        child.parent = weakref.ref(self)
        self.children.append(child)

    def __str__(self):
        return " + {0}".format(self.text)


class ContainerItem(Item):
    """This item is only active if it has children."""

    @property
    def active(self):
        # print("active???", self, len(self.children))
        # return True
        return len(self.children) > 0


class InactiveItem(Item):

    def __init__(self, text):
        super().__init__(text, active=False)

    def __str__(self):
        return " ( {0} )".format(self.text)


class Model:

    def __init__(self, show_all=False):
        self.items = []
        self.show_all = show_all

    def add(self, item):
        # if item.active or self.show_all:
        if True:
            if item.parent:
                for i in range(len(self.items) - 1, -1, -1):
                    if self.items[0].parent == item.parent or \
                            self.items[0] == item.parent:
                        self.items.insert(i + 1, item)
                        break
                else:
                    self.items.append(item)
            else:
                self.items.append(item)
        return item

    def remove(self, item):
        self.items.remove(item)
        return item

    def last_item(self):
        return self.items[-1]


def normalize(value):
    n = ""
    for c in value.lower():
        if c in "abcdefghijklmnopqrstuvwxyz0123456789+":
            n += c
    return n


def create_joystick_port_item(c, num: int) -> Item:
    # FIXME: retrieve uae_ option
    mode = c.get("joystick_port_{0}_mode".format(num))
    if mode == "nothing":
        item = InactiveItem("Joystick Port {0}".format(num))
    else:
        item = Item("Joystick Port {0}".format(num))

        if mode == "joystick":
            device_text = "[J]"
        elif mode == "mouse":
            device_text = "[M]"
        elif mode == "cd32_gamepad":
            device_text = "[C]"
        else:
            device_text = "[?]"
        # FIXME: auto-calculated device
        device = c.get("joystick_port_{0}".format(num))
        if not device:
            device = "???"
        device_text += " " + device

        device_item = Item(device_text)
        item.add(device_item)

    return item


def create_slirp_item(c):
    implementation = c.uae_slirp_implementation
    if implementation == "auto":
        name = "Auto"
    elif implementation == "none":
        name = "None"
    elif implementation == "builtin":
        name = "Built-in"
    elif implementation == "qemu":
        name = "QEMU"
    else:
        name = implementation
    slirp_item = Item("Slirp ({})".format(name))

    if c.uae_slirp_ports:
        slirp_ports_item = Item("Ports: " + c.uae_slirp_ports)
        slirp_item.add(slirp_ports_item)
    if c.uae_slirp_redir:
        slirp_redir_item = Item("Redirect: " + c.uae_slirp_redir)
        slirp_item.add(slirp_redir_item)

    return slirp_item


def create_model(c, show_all=False):
    model = Model(show_all=show_all)

    # if c.ntsc_mode:
    #     model_item = Item(c.int_model_name + " NTSC")
    # else:
    #     model_item = Item(c.int_model_name + " PAL")
    # model_item.represents = ["amiga_model", "ntsc_mode"]
    # model.add(model_item)

    text = c.int_chipset_name
    if c.uae_chipset_compatible != "-":
        text += " ({0})".format(c.uae_chipset_compatible)
    if c.ntsc_mode:
        text += " NTSC"
    else:
        text += " PAL"
    chipset_item = Item(text)
    chipset_item.represents = ["uae_chipset", "uae_chipset_compatible",
                               "ntsc_mode"]
    model.add(chipset_item)

    if c.uae_chipset == "aga":
        text = "Alice (AGA)"
        if c.ntsc_mode:
            text += " NTSC"
        else:
            text += " PAL"
        alice_item = Item(text)
        chipset_item.add(alice_item)
        lisa_item = Item("Lisa (AGA)")
        chipset_item.add(lisa_item)
        paula_item = Item("Paula (AGA)")
        chipset_item.add(paula_item)
    else:

        # http://en.wikipedia.org/wiki/MOS_Technology_Agnus
        if c.uae_chipset in ["ecs_agnus", "ecs"]:
            text = "Agnus (ECS)"
        else:
            text = "Agnus"
        if c.ntsc_mode:
            text += " NTSC"
        else:
            text += " PAL"
        agnus_item = Item(text)
        chipset_item.add(agnus_item)

        if c.uae_chipset in ["ecs_denise", "ecs"]:
            denise_item = Item("Denise (ECS)")
        else:
            denise_item = Item("Denise")
        chipset_item.add(denise_item)
        if c.uae_chipset in ["ecs"]:
            paula_item = Item("Paula")
        else:
            paula_item = Item("Paula")
        chipset_item.add(paula_item)

    if c.uae_cd32cd == "true":
        akiko_item = Item("Akiko")
        chipset_item.add(akiko_item)

    # if c.kickstart_file:
    #     kickstart_item = Item("Custom Kickstart [FIXME]")
    # else:
    #     kickstart_item = Item("Default Kickstart [FIXME]")
    kickstart_item = Item("Kickstart {} Rev {}".format(
        c.int_kickstart_version, c.int_kickstart_revision))
    model.add(kickstart_item)

    if c.int_kickstart_ext_sha1 == "5bef3d628ce59cc02a66e6e4ae0da48f60e78f7f":
        kickstart_ext_item = Item("CD32 Extended ROM")
    elif c.int_kickstart_ext_sha1 == "7ba40ffa17e500ed9fed041f3424bd81d9c907be":
        kickstart_ext_item = Item("CDTV Extended ROM")
    else:
        kickstart_ext_item = InactiveItem("Extended ROM")
    model.add(kickstart_ext_item)

    cpu_item = Item("MC" + c.int_cpu_name)
    cpu_item.represents = ["cpu", "uae_cpu_model"]  # FIXME: uae_cpu_type

    if c.int_accelerator_name:
        item = Item("{0} [Accelerator]".format(c.int_accelerator_name))
        accelerator_item = model.add(item)
    else:
        accelerator_item = InactiveItem("No Accelerator")
        model.add(accelerator_item)
    accelerator_item.represents = ["accelerator", "uae_cpuboard_type"]

    if accelerator_item.active:
        accelerator_item.add(cpu_item)
    else:
        model.add(cpu_item)

    if accelerator_item.active:
        if c.int_ppc_model:
            item = Item("PowerPC {0} [PPC CPU]".format(c.int_ppc_model))
            accelerator_item.add(item)

        # model.remove(cpu_item)
        # cpu_item.set_parent(accelerator_item)
        # model.add(cpu_item)

        if c.int_cpuboardmem1_size:
            size = "{0} MB".format(int(c.int_cpuboardmem1_size) //
                                   (1024 * 1024))
            item = Item("{0} RAM".format(size))
            item.represents = ["uae_cpuboard1mem_size"]
            accelerator_item.add(item)

        item = Item("ROM/Flash [FIXME]")
        item.represents = ["accelerator_rom"]
        accelerator_item.add(item)

        if c.uae_cpuboard_type == "CyberStormPPC":
            # FIXME: other too?
            accelerator_scsi_item = Item("CyberStorm SCSI")
            accelerator_item.add(accelerator_scsi_item)

    if int(c.uae_mmu_model):
        mmu_item = Item("{0} MMU".format(c.uae_mmu_model))
    else:
        mmu_item = InactiveItem("No MMU")
    cpu_item.represents = ["mmu_model"]
    cpu_item.add(mmu_item)

    if int(c.uae_fpu_model):
        fpu_item = Item("{0} FPU".format(c.uae_fpu_model))
    else:
        fpu_item = InactiveItem("No FPU")
        # fpu_item.set_parent(cpu_item)
    fpu_item.represents = ["fpu_model"]
    if c.uae_fpu_model == c.uae_cpu_model:
        cpu_item.add(fpu_item)
    else:
        model.add(fpu_item)

    if int(c.int_chipmem_size) % (1024 * 1024) == 0:
        size = "{0} MB".format(int(c.int_chipmem_size) // (1024 * 1024))
    else:
        size = "{0} KB".format(int(c.int_chipmem_size) // 1024)
    chipmem_item = Item("{0} Chip RAM".format(size))
    chipmem_item.represents = ["chip_memory", "uae_chipmem_size"]
    model.add(chipmem_item)

    if int(c.int_mbresmem_low_size):
        size = "{0} MB".format(int(c.int_mbresmem_low_size) // (1024 * 1024))
        item = Item("{0} Fast RAM".format(size))
    else:
        item = InactiveItem("No Fast RAM")
    item.extra = "Motherboard"
    item.represents = ["uae_a3000mem_size"]
    model.add(item)

    trapdoor_item = ContainerItem("Trapdoor Slot")
    zorro_ii_item = ContainerItem("Zorro II Bus")
    zorro_iii_item = ContainerItem("Zorro III Bus")

    flatten = True

    if int(c.int_bogomem_size):
        if int(c.int_bogomem_size) % (1024 * 1024) == 0:
            size = "{0} MB".format(int(c.int_bogomem_size) // (1024 * 1024))
        else:
            size = "{0} KB".format(int(c.int_bogomem_size) // 1024)
        bogomem_item = Item("{0} Slow RAM".format(size))
    else:
        bogomem_item = InactiveItem("No Slow RAM")
    bogomem_item.represents = ["slow_memory", "uae_bogomem_size"]
    if flatten:
        bogomem_item.extra = "Trapdoor"
        model.add(bogomem_item)
    else:
        trapdoor_item.add(bogomem_item)

    if int(c.int_fastmem_size):
        if int(c.int_fastmem_size) % (1024 * 1024) == 0:
            size = "{0} MB".format(int(c.int_fastmem_size) // (1024 * 1024))
        else:
            size = "{0} KB".format(int(c.int_fastmem_size) // 1024)
        # fastmem_item = Item("{0} Zorro II Fast RAM".format(size))
        fastmem_item = Item("{0} Fast RAM".format(size))
    else:
        fastmem_item = InactiveItem("No Zorro II Fast RAM")
    fastmem_item.represents = ["fast_memory", "uae_fastmem_size"]
    if flatten:
        fastmem_item.extra = "Zorro II"
        model.add(fastmem_item)
    else:
        zorro_ii_item.add(fastmem_item)

    if int(c.int_z3fastmem_size):
        size = "{0} MB".format(int(c.int_z3fastmem_size) // (1024 * 1024))
        # z3fastmem_item = Item("{0} Zorro III Fast RAM".format(size))
        z3fastmem_item = Item("{0} Fast RAM".format(size))
    else:
        z3fastmem_item = InactiveItem("No Zorro III Fast RAM")
    z3fastmem_item.represents = ["zorro_iii_memory", "uae_z3mem_size"]
    if flatten:
        z3fastmem_item.extra = "Zorro III"
        model.add(z3fastmem_item)
    else:
        zorro_iii_item.add(z3fastmem_item)

    if c.uae_rtc != "none":
        rtc_item = Item("{0} RTC".format(c.uae_rtc))
    else:
        rtc_item = InactiveItem("No Real Time Clock")
    rtc_item.represents = ["uae_rtc"]
    if bogomem_item.active and c.uae_rtc == "MSM6242B":
        if flatten:
            # bogomem_item.add(rtc_item)
            model.add(rtc_item)
        else:
            trapdoor_item.add(rtc_item)
    else:
        model.add(rtc_item)

    if c.uae_cd32fmv == "true":

        fmv_item = Item("CD32 FMV Module")
        model.add(fmv_item)

        fmv_rom_item = Item("CD32 FMV ROM")
        fmv_item.add(fmv_rom_item)

    model.add(trapdoor_item)
    model.add(zorro_ii_item)
    model.add(zorro_iii_item)

    resident_item = ContainerItem("Resident Libraries")
    model.add(resident_item)

    if c.int_uae_boot_rom == "true":
        uae_boot_rom_item = Item("UAE Boot ROM")
        resident_item.add(uae_boot_rom_item)

        uae_resource_item = Item("uae.resource")
        uae_boot_rom_item.add(uae_resource_item)

        if c.uae_bsdsocket_emu == "true":
            bsdsocket_item = Item("bsdsocket.library")
        else:
            bsdsocket_item = InactiveItem("No bsdsocket.library")
        bsdsocket_item.represents = ["bsdsocket_library",
                                     "uae_bsdsocket_emu"]
        resident_item.add(bsdsocket_item)

        if c.uae_native_code == "true":
            uaenative_library_item = Item("uaenative.library")
        else:
            uaenative_library_item = InactiveItem("No uaenative.library")
        uaenative_library_item.represents = ["uaenative.library",
                                             "uae_native_code"]
        resident_item.add(uaenative_library_item)

        if c.uae_sana2 == "true":
            uaenet_device_item = Item("uaenet.device")
        else:
            uaenet_device_item = InactiveItem("No uaenet.device")
        uaenet_device_item.represents = ["uae_sana2"]
        resident_item.add(uaenet_device_item)

    if c.uae_a2065:
        a2065_item = Item("A2065 [Network Card]")
        a2065_item.represents = ["uae_a2065"]
        zorro_ii_item.add(a2065_item)

        if c.uae_a2065 == "slirp":
            slirp_item = create_slirp_item(c)
            a2065_item.add(slirp_item)

    if c.uae_gfxcard_type:
        graphics_card_item = Item("{} {} MB".format(
            c.int_graphics_card_name, c.uae_gfxcard_size))
        if flatten:
            if c.int_graphics_card_bus == "zorro-ii":
                graphics_card_item.extra = "Zorro II"
            elif c.int_graphics_card_bus == "zorro-iii":
                graphics_card_item.extra = "Zorro III"
            model.add(graphics_card_item)
        elif c.int_graphics_card_bus == "zorro-ii":
            zorro_ii_item.add(graphics_card_item)
        elif c.int_graphics_card_bus == "zorro-iii":
            zorro_iii_item.add(graphics_card_item)
        else:
            model.add(graphics_card_item)

    if c.uae_toccata == "true":
        sound_card_item = Item("Toccata")
        sound_card_item.represents = ["sound_card", "uae_toccata"]
        if flatten:
            sound_card_item.extra = "Zorro II"
            model.add(sound_card_item)
        else:
            zorro_ii_item.add(sound_card_item)

    joystick_port_0_item = create_joystick_port_item(c, 0)
    joystick_port_1_item = create_joystick_port_item(c, 1)
    joystick_port_2_item = create_joystick_port_item(c, 2)
    joystick_port_3_item = create_joystick_port_item(c, 3)

    model.add(joystick_port_0_item)
    model.add(joystick_port_1_item)
    # parallel_port_item = Item("Parallel Port")

    if joystick_port_2_item.active or joystick_port_3_item.active:
        parallel_port_item = Item("Parallel Port Joystick Adapter")
        model.add(parallel_port_item)
        parallel_port_item.add(joystick_port_2_item)
        parallel_port_item.add(joystick_port_3_item)
    else:
        parallel_port_item = InactiveItem("No Parallel Port Device")
        model.add(parallel_port_item)

    for i in range(4):
        type = getattr(c, "uae_floppy{0}type".format(i))
        if type == "0":
            description = "3.5\" DD"
        elif type == "1":
            description = "3.5\" HD"
        elif type == "2":
            description = "5.25\" SD"
        elif type == "3":
            description = "3.5\" DD (ESCOM)"
        else:
            description = None
        if description:
            drive_item = Item("{0} Floppy Drive [DF{1}]".format(
                description, i))
        else:
            drive_item = InactiveItem("No Floppy Drive [DF{0}]".format(i))
        drive_item.represents = [
            "floppy_drive_{0}".format(i),
            "uae_df{0}type".format(i),
        ]
        model.add(drive_item)

        path = getattr(c, "uae_floppy{0}".format(i))
        if path:
            name = os.path.basename(path)
            disk_item = Item(name)
            drive_item.add(disk_item)

    return model
