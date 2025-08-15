import k_lights_interface.k_device_names as kdn


class KCapabilities:
    def __init__(self, number_of_led_colors=6, minimum_duv=-0.027, maximum_duv=0.027, minimum_kelvin=2000, maximum_kelvin=20000,
                 min_white_point=2800, max_white_point=10000,
                 min_kelvin_gel_mode=2800, max_kelvin_gel_mode=10000,
                 channel_ordering=["lime", "blue", "red", "green", "cyan", "amber"],
                 number_of_fans=0,
                 has_mcumgr_serial=False,
                 watt_draw_per_output=None,
                 max_specified_watt_draw=None,
                 has_driver_temp_dependant_transistor=False
                 ):
        self.number_of_led_colors = number_of_led_colors
        self.minimum_duv = minimum_duv
        self.maximum_duv = maximum_duv
        self.minimum_kelvin = minimum_kelvin
        self.maximum_kelvin = maximum_kelvin
        self.min_white_point = min_white_point
        self.max_white_point = max_white_point
        self.min_kelvin_gel_mode = min_kelvin_gel_mode
        self.max_kelvin_gel_mode = max_kelvin_gel_mode
        self.channel_ordering = channel_ordering
        self.number_of_fans = number_of_fans
        self.has_mcumgr_serial = has_mcumgr_serial
        self.watt_draw_per_output = watt_draw_per_output
        self.max_specified_watt_draw = max_specified_watt_draw
        self.has_driver_temp_dependant_transistor = has_driver_temp_dependant_transistor

    def calc_ch_output(self, desired_watt_draw) -> float | None:
        """Calculate required output for each channel of the light to achieve desired watt draw

        Args:
            desired_watt_draw (_type_): 

        Returns:
            float | None: 
        """
        if self.watt_draw_per_output is None:
            return None
        base_watt_draw = sum(self.watt_draw_per_output)
        if base_watt_draw == 0:
            return None
        output = desired_watt_draw / base_watt_draw
        return output
    

k_capabilities = {kdn.play_device_name: KCapabilities(has_mcumgr_serial=True, watt_draw_per_output=[0.1, 0.1, 0.1, 0.1, 0.073, 0.1], max_specified_watt_draw=10, has_driver_temp_dependant_transistor=True),
                  kdn.play_pro_device_name: KCapabilities(has_mcumgr_serial=True, watt_draw_per_output=[0.1, 0.1, 0.1, 0.1, 0.073, 0.1], max_specified_watt_draw=10, has_driver_temp_dependant_transistor=True),
                  kdn.play_hero_device_name: KCapabilities(has_mcumgr_serial=True, watt_draw_per_output=[0.1, 0.1, 0.1, 0.1, 0.073, 0.1], max_specified_watt_draw=10, has_driver_temp_dependant_transistor=True),
                  kdn.epos_300_lamphead_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2, watt_draw_per_output=[1.02, 0.875, 1.59, 0.275, 0.383, 0.645], max_specified_watt_draw=300),
                  kdn.epos_300_controller_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2),
                  kdn.epos_600_lamphead_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2, has_mcumgr_serial=True, watt_draw_per_output=[1.02, 0.875, 1.59, 0.275, 0.383, 0.645], max_specified_watt_draw=600),
                  kdn.epos_600_controller_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2, has_mcumgr_serial=True),
                  kdn.photosynthetic_grow_light_v1: KCapabilities(number_of_led_colors=4)
                  }
