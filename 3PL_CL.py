import pandas as pd

class FreightPricingEngine:
    def __init__(self):
        # Industry Standard Levers
        self.dim_factor_domestic = 194  # standard domestic inches/lb
        self.fuel_peg_price = 3.50      # base fuel price in contract
        self.fuel_efficiency_mpg = 6.5  # average Class 8 truck MPG
        
    def calculate_dim_weight(self, length, width, height):
        """Calculates Dimensional Weight to prevent margin leakage on bulky cargo."""
        return (length * width * height) / self.dim_factor_domestic

    def get_fuel_surcharge(self, current_fuel_price, distance):
        """Index-Linked Fuel Surcharge calculation."""
        if current_fuel_price <= self.fuel_peg_price:
            return 0
        fuel_diff = current_fuel_price - self.fuel_peg_price
        return (fuel_diff / self.fuel_efficiency_mpg) * distance

    def calculate_quote(self, mode, actual_weight, dims, distance, fuel_price, equipment_type="Dry Van"):
        """
        Main Pricing Lever Engine
        Modes: 'LTL' (Less-than-Truckload), 'FTL' (Full Truckload)
        """
        # 1. Determine Chargeable Weight
        l, w, h = dims
        dim_weight = self.calculate_dim_weight(l, w, h)
        chargeable_weight = max(actual_weight, dim_weight)

        # 2. Base Rate Logic (Simplified for Template)
        if mode == 'FTL':
            base_rate_per_mile = 2.50
            equipment_multiplier = 1.3 if equipment_type == "Reefer" else 1.0
            subtotal = (distance * base_rate_per_mile) * equipment_multiplier
        else: # LTL Logic
            rate_per_cwt = 15.00 # Rate per 100 lbs
            subtotal = (chargeable_weight / 100) * rate_per_cwt

        # 3. Apply FSC (Fuel Surcharge)
        fsc = self.get_fuel_surcharge(fuel_price, distance)
        
        total_landed_cost = subtotal + fsc
        
        return {
            "Mode": mode,
            "Chargeable Weight": round(chargeable_weight, 2),
            "Base Freight": round(subtotal, 2),
            "Fuel Surcharge": round(fsc, 2),
            "Total Landed Cost": round(total_landed_cost, 2)
        }

# --- Example Implementation ---
engine = FreightPricingEngine()

# Scenario: 500-mile Reefer FTL run with current diesel at $4.20
quote = engine.calculate_quote(
    mode='FTL', 
    actual_weight=42000, 
    dims=(636, 102, 110), # Standard 53' trailer dims
    distance=500, 
    fuel_price=4.20,
    equipment_type="Reefer"
)

print(pd.DataFrame([quote]))
