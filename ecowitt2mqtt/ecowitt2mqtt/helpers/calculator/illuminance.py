"""Define illuminance calculators."""

from __future__ import annotations

from typing import cast

from ecowitt2mqtt.const import (
    CONF_OUTPUT_UNIT_ILLUMINANCE,
    DATA_POINT_SOLARRADIATION,
    PERCENTAGE,
    UnitOfIlluminance,
)
from ecowitt2mqtt.helpers.calculator import CalculatedDataPoint, Calculator, SimpleCalculator
from ecowitt2mqtt.helpers.typing import PreCalculatedValueType
from ecowitt2mqtt.util.unit_conversion import IlluminanceConverter


class BaseSolarRadiationCalculator(Calculator):
    """Define a base illuminance calculator."""

    DEFAULT_INPUT_UNIT = UnitOfIlluminance.WATTS_PER_SQUARE_METER


class SolarRadiationCalculator(SimpleCalculator):
    """Define a solar radiation calculator."""

    @property
    def output_unit(self) -> str:
        """Get the output unit of measurement for this calculation.

        Returns:
            A unit string.
        """
        return UnitOfIlluminance.WATTS_PER_SQUARE_METER


class IlluminanceCalculator(BaseSolarRadiationCalculator):
    """Define an illuminance calculator."""
    
    UNIT_OVERRIDE_CONFIG_OPTION = CONF_OUTPUT_UNIT_ILLUMINANCE
    
    @property
    def output_unit_imperial(self) -> str:
        """Get the default unit (imperial).

        Returns:
            A unit string.
        """
        return UnitOfIlluminance.LUX

    @property
    def output_unit_metric(self) -> str:
        """Get the default unit (metric).

        Returns:
            A unit string.
        """
        return UnitOfIlluminance.LUX

    @Calculator.requires_keys(DATA_POINT_SOLARRADIATION)
    def calculate_from_payload(
        self, payload: dict[str, PreCalculatedValueType]
    ) -> CalculatedDataPoint:
        """Perform the calculation.

        Args:
            payload: An Ecowitt data payload.

        Returns:
            A parsed CalculatedDataPoint object.
        """
        solar_rad = cast(float, payload[DATA_POINT_SOLARRADIATION])
        return self.get_calculated_data_point(
            solar_rad, unit_converter=IlluminanceConverter
        )


class IlluminancePerceptionCalculator(BaseSolarRadiationCalculator):
    """Define an illuminance perception calculator."""

    @property
    def output_unit(self) -> str:
        """Get the output unit of measurement for this calculation.

        Returns:
            A unit string.
        """
        return PERCENTAGE

    @Calculator.requires_keys(DATA_POINT_SOLARRADIATION)
    def calculate_from_payload(
        self, payload: dict[str, PreCalculatedValueType]
    ) -> CalculatedDataPoint:
        """Perform the calculation.

        Args:
            payload: An Ecowitt data payload.

        Returns:
            A parsed CalculatedDataPoint object.
        """
        solar_rad = cast(float, payload[DATA_POINT_SOLARRADIATION])
        return self.get_calculated_data_point(
            solar_rad, unit_converter=IlluminanceConverter
        )


class IlluminancePerceivedCalculator(BaseSolarRadiationCalculator):
    """Define an illuminance perceived calculator."""

    DEFAULT_INPUT_UNIT = UnitOfIlluminance.LUX
    UNIT_OVERRIDE_CONFIG_OPTION = CONF_OUTPUT_UNIT_ILLUMINANCE

    @property
    def output_unit_imperial(self) -> str:
        """Get the default unit (imperial).

        Returns:
            A unit string.
        """
        return UnitOfIlluminance.LUX

    @property
    def output_unit_metric(self) -> str:
        """Get the default unit (metric).

        Returns:
            A unit string.
        """
        return UnitOfIlluminance.LUX

    @Calculator.requires_keys(DATA_POINT_SOLARRADIATION)
    def calculate_from_payload(
        self, payload: dict[str, PreCalculatedValueType]
    ) -> CalculatedDataPoint:
        """Perform the calculation.

        Args:
            payload: An Ecowitt data payload.

        Returns:
            A parsed CalculatedDataPoint object.
        """
        solar_rad = cast(float, payload[DATA_POINT_SOLARRADIATION])

        # 1. Calculate Illuminance (lx) from Solar Radiation (W/m²)
        lux = IlluminanceConverter.convert(
            solar_rad, 
            UnitOfIlluminance.WATTS_PER_SQUARE_METER, 
            UnitOfIlluminance.LUX
        )

        # 2. Calculate Illuminance Perception (%) from Solar Radiation (W/m²)
        # Note: IlluminanceConverter.convert handles % calculation via log10 logic
        perception_pct = IlluminanceConverter.convert(
            solar_rad, 
            UnitOfIlluminance.WATTS_PER_SQUARE_METER, 
            PERCENTAGE
        )

        # 3. Calculate perceived value in Lux
        perceived_lux = lux * (perception_pct / 100.0)

        # 4. Use helper to convert perceived_lux to the user's preferred unit (fc, klx, etc.)
        return self.get_calculated_data_point(
            perceived_lux, unit_converter=IlluminanceConverter
        )