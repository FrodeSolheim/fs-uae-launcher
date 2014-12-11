from .mess import MESSRunner


class ZXSpectrumRunner(MESSRunner):

    JOYSTICK = {
        "type": "joystick",
        "description": "Joystick",
        "mapping_name": "zx-spectrum-joystick",
    }

    PORTS = [
        {
            "description": "Joystick Port",
            "types": [JOYSTICK]
        },
    ]

    def mess_configure(self):
        # FIXME: hack
        # self.mess_configure_floppies(["cassette"])

        if self.config["snapshot"]:
            # snapshot loads automatically, no need to do anything special
            self.add_arg("-{0}".format("snapshot"),
                         self.get_game_file("snapshot"))
        elif self.config["floppy_drive"]:
            # pressing enter to select "loader" in the menu
            self.inject_fake_input_string(160, "{0}\n".format(""))
            self.add_arg("-{0}".format("floppydisk1"),
                         self.get_game_file("floppy_drive"))
        elif self.config["tape_drive"]:
            self.inject_fake_input_string_list(160, [
                "1106", "0106", "0000",  # j (LOAD)
                "1032", "0032", "0000",  # space
                "1303", "0000",          # right shift (press)
                "1112", "0112", "0000",  # p (with symbol shift = ")
                "0303", "0000",          # right shift (release)
                "1303", "0000",          # right shift (press)
                "1112", "0112", "0000",  # p (with symbol shift = ")
                "0303", "0000",          # right shift (release)
                "1013", "0013", "0000",  # return
            ])
            self.add_arg("-{0}".format("cassette"),
                         self.get_game_file("tape_drive"))

    def mess_full_keyboard(self):
        return True

    def mess_input_mapping(self, port):
        return {
            "UP": 'tag=":KEMPSTON" type="KEYBOARD" mask="8" defvalue="0"',
            "DOWN": 'tag=":KEMPSTON" type="KEYBOARD" mask="4" defvalue="0"',
            "LEFT": 'tag=":KEMPSTON" type="KEYBOARD" mask="2" defvalue="0"',
            "RIGHT": 'tag=":KEMPSTON" type="KEYBOARD" mask="1" defvalue="0"',
            "1": 'tag=":KEMPSTON" type="KEYBOARD" mask="16" defvalue="0"',
        }

    def get_game_refresh_rate(self):
        # Refresh rate values retrieved from MESS
        if self.config["model"] == "spectrum128":
            return 50.021084
        else:
            return 50.080128

    def mess_romset(self):
        # MESS system names:
        # sp3e8bit          ZX Spectrum +3e 8bit IDE
        # sp3eata           ZX Spectrum +3e 8bit ZXATASP
        # sp3ezcf           ZX Spectrum +3e 8bit ZXCF
        # spec128           ZX Spectrum 128
        # spec80k           ZX Spectrum 80K
        # specide           ZX Spectrum IDE
        # specpl2a          ZX Spectrum +2a
        # specpl3e          ZX Spectrum +3e
        # specpls2          ZX Spectrum +2
        # specpls3          ZX Spectrum +3
        # spectrum          ZX Spectrum
        if self.config["model"] == "spectrum128":
            return "spec128", SPEC128_ROMS
        if self.config["model"] == "spectrum+3":
            return "specpls3", SPECPLS3_ROMS
        else:
            return "spectrum", SPECTRUM_ROMS


SPECTRUM_ROMS = [
    ("f9d23f25640c51bcaa63e21ed5dd66bb2d5f63d4", "1986es.rom"),
    ("9e535e2e24231ccb65e33d107f6d0ceb23e99477", "48e.rom"),
    ("e62a431b0938af414b7ab8b1349a18b3c4407f70", "48turbo.rom"),
    ("ab3c36daad4325c1d3b907b6dc9a14af483d14ec", "bsrom118.rom"),
    ("2ee2dbe6ab96b60d7af1d6cb763b299374c21776", "bsrom140.rom"),
    ("795c20324311dd5a56300e6e4ec49b0a694ac0b3", "deutsch.rom"),
    ("51165cde68e218512d3145467074bc7e786bf307", "groot.rom"),
    ("a701c3d4b698f7d2be537dc6f79e06e4dbc95929", "gw03.rom"),
    ("2a9745ba3b369a84c4913c98ede66ec87cb8aec1", "hdt-iso.rom"),
    ("dee814271c4d51de257d88128acdb324fb1d1d0d", "imc.rom"),
    ("5752e6f789769475711b91e0a75911fa5232c767", "iso8bm.rom"),
    ("04adbdb1380d6ccd4ab26ddd61b9ccbba462a60f", "isomoje.rom"),
    ("d7f02ed66455f1c08ac0c864c7038a92a88ba94a", "jgh.rom"),
    ("c103e89ef58e6ade0c01cea0247b332623bd9a30", "plus4.rom"),
    ("0853e25857d51dd41b20a6dbc8e80f028c5befaa", "psycho.rom"),
    ("c58ff44a28db47400f09ed362ca0527591218136", "sc01.rom"),
    ("5ea7c2b824672e914525d1d5c419d71b84a426a2", "spectrum.rom"),
    ("84ea64af06adaf05e68abe1d69454b4fc6888505", "turbo2_3.rom"),
    ("21ad93ffe41a4458704c866cca2754f066f6a560", "turbo4_4.rom"),
]


SPEC128_ROMS = [
    ("4f4b11ec22326280bdb96e3baf9db4b4cb1d02c5", "zx128_0.rom"),
    ("80080644289ed93d71a1103992a154cc9802b2fa", "zx128_1.rom"),
    ("968937b1c750f0ef6205f01c6db4148da4cca4e3", "zx128s0.rom"),
    ("bea3f397cc705eafee995ea629f4a82550562f90", "zx128s1.rom"),
]


SPECPLS3_ROMS = [
    ("4e5d114b72d464cefdde0566457f52a3c0c1cae2", "p3_01_4m.rom"),
    ("4e5d114b72d464cefdde0566457f52a3c0c1cae2", "p3_01_cm.rom"),
    ("752cdd6a083ab9910348995e483541d60bb6372b", "p3_23_4m.rom"),
    ("d062765ceb1f3cd2c94ea51cb737cac7ad6151b4", "p3_23_cm.rom"),
    ("e319ed08b4d53a5e421a75ea00ea02039ba6555b", "pl3-0.rom"),
    ("c9969fc36095a59787554026a9adc3b87678c794", "pl3-1.rom"),
    ("22e50c6ba4157a3f6a821bd9937cd26e292775c6", "pl3-2.rom"),
    ("65f031caa8148a5493afe42c41f4929deab26b4e", "pl3-3.rom"),
    ("500c0945760abeefcbd08bc22c0d07b14b336cf0", "plus341.rom"),
    ("e9b0a60a1a8def511d59090b945d175bdc646346", "plus3sp0.rom"),
    ("4e48f196427596c7990c175d135c15a039c274a4", "plus3sp1.rom"),
    ("09fc005625589ef5992515957ce7a3167dec24b2", "plus3sp2.rom"),
    ("ec8f644a81e2e9bcb58ace974103ea960361bad2", "plus3sp3.rom"),
]
