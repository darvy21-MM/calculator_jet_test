class SalaryCalculator:
    def __init__(self, ral, contract_type, agevolazioni, detrazioni, ccnl_sector):
        self.ral = ral
        self.contract_type = contract_type
        self.agevolazioni = agevolazioni if contract_type != "collaboratore" else "nessuna agevolazione"
        self.detrazioni = detrazioni
        self.ccnl_sector = ccnl_sector
    
        
        self.MAX_INPS = 119650
        self.SOGLIA_IVS = 55008
        
        self.ALIQUOTA_AZIENDA = {
            "Call Center": {"indeterminato": 0.2381, "determinato": 0.2521, "apprendistato": 0.1161, "collaboratore": 0.2335},
            "Commercio e Terziario": {"indeterminato": 0.2998, "determinato": 0.3138, "apprendistato": 0.1161, "collaboratore": 0.2335},
            "Industria Metalmeccanica": {"indeterminato": 0.2998, "determinato": 0.3138, "apprendistato": 0.1161, "collaboratore": 0.2335}
    
        }
        
        self.COEF_INPS_DIP = {"indeterminato": 0.0919, "determinato": 0.0919, "apprendistato": 0.0584}
        
        self.ALIQUOTA_IRPEF = [(15000, 0.23), (28000, 0.23), (50000, 0.35), (float("inf"), 0.43)]
        
        self.INAIL_RATE = 0.004
        
        self.ALIQUOTA_ADD_COM = 0.008  # Milano
        self.ADDIZIONALE_REGIONALE = [(15000, 0.0123), (28000, 0.0158), (50000, 0.0172), (float("inf"), 0.0173)]
        
        self.IRPEF_BRACKETS = [(15000, 0.23), (28000, 0.23), (50000, 0.35), (float("inf"), 0.43)]

    def apply_esonero_inps(self, inps_tot):
        if self.agevolazioni == "under 36":
            return inps_tot - min(8000, inps_tot * 0.5)
        elif self.agevolazioni == "under 30":
            return inps_tot - min(3000, inps_tot * 0.5)
        elif self.agevolazioni == "donne":
            return min(6000, inps_tot * 0.5)
        elif self.agevolazioni == "over 50":
            return inps_tot * 0.5
        return inps_tot
    
    def calculate_irpef(self, imponibile):
        irpef = 0
        brackets = [15000, 28000, 50000]
        rates = [0.23, 0.23, 0.35, 0.43]
        prev_bracket = 0
        
        for i, bracket in enumerate(brackets + [float("inf")]):
            if imponibile > prev_bracket:
                taxable = min(imponibile, bracket) - prev_bracket
                irpef += taxable * rates[i]
            prev_bracket = bracket
        
        return irpef

    def calculate_detrazione_spettante(self, imponibile):
        detrazione = 0
        bracket_values = {"1st_bracket": 0, "2nd_bracket": 0, "3rd_bracket": 0, "4th_bracket": 0, "bonus": 0}
        
        if imponibile <= 15000:
            bracket_values["1st_bracket"] = 1955
        if 15000 < imponibile <= 28000:
            bracket_values["2nd_bracket"] = 1910 + (1190 * (28000 - imponibile) / 13000)
        if 28000 < imponibile <= 50000:
            bracket_values["3rd_bracket"] = 1910 * ((50000 - imponibile) / 22000)
        if 25000 <= imponibile <= 35000:
            bracket_values["bonus"] = 65
        
        detrazione = sum(bracket_values.values())
        return detrazione
    
    def calculate_trattamento_integrativo(self, imponibile, irpef_lorda, detrazioni_spett):
        if imponibile < 15000:
            return 1200
        elif 15000 < imponibile < 28000 and irpef_lorda < detrazioni_spett:
            return min(1200, detrazioni_spett - irpef_lorda)
        return 0
    
    def calculate_irpef_netta(self, irpef_lorda, detrazioni_spett, imponibile_irpef):
            detrazione_L207 = self.calculate_detrazione_L207_2024(imponibile_irpef)
            return max(0, irpef_lorda - detrazioni_spett - detrazione_L207)

    
    def calculate_detrazione_L207_2024(self, imponibile):
        if imponibile < 40000:
            if imponibile <= 32000:
                return 1000 if imponibile > 20000 else 0
            return (40000 - imponibile) / 8
        return 0
    
    def calculate_inps_dipendente(self):
        if self.contract_type in ["indeterminato", "determinato", "apprendistato"]:
            return self.ral * self.COEF_INPS_DIP[self.contract_type]
        elif self.contract_type == "collaboratore":
            return (self.ral * 0.3503) / 3
        return 0

    def calculate_inps_azienda(self):
        aliquota = self.ALIQUOTA_AZIENDA[self.ccnl_sector][self.contract_type]
        if self.ral < self.MAX_INPS:
            inps_tot = self.ral * aliquota
        else:
            inps_tot = (self.MAX_INPS * aliquota) + (self.ral - self.MAX_INPS) * 0.01
        return self.apply_esonero_inps(inps_tot)
    
    
    def calculate_tfr(self):
        if self.contract_type == "collaboratore":
            return 0
        return (self.ral / 13.5) + (self.ral * (0.015 + (0.017 * 0.75)))
    
    def calculate_addizionale_regionale(self, imponibile):
        addizionale = 0
        prev_bracket = 0
        for bracket, rate in self.ADDIZIONALE_REGIONALE:
            if imponibile > prev_bracket:
                taxable = min(imponibile, bracket) - prev_bracket
                addizionale += taxable * rate
            prev_bracket = bracket
        return addizionale
    
    def calculate_stipendio_netto(self):
        print("✅ Debug: Inside SalaryCalculator")

        inps_dip = self.calculate_inps_dipendente()
        inps_azienda = self.calculate_inps_azienda()
        inail = self.ral * self.INAIL_RATE
        tfr = self.calculate_tfr()
        imponibile_base = self.ral - inps_dip

        if self.detrazioni == "bonus rimpatriati":
            imponibile_irpef = imponibile_base * 0.5
        elif self.detrazioni == "bonus rimpatriati con figli":
            imponibile_irpef = imponibile_base * 0.4
        else:
            imponibile_irpef = imponibile_base

        addizionale_comunale = imponibile_irpef * self.ALIQUOTA_ADD_COM
        addizionale_regionale = self.calculate_addizionale_regionale(imponibile_irpef)
        irpef = self.calculate_irpef(imponibile_irpef)
        irpef_lorda =  irpef + addizionale_comunale + addizionale_regionale
        detrazioni_spett = self.calculate_detrazione_spettante(imponibile_irpef)
        trattamento_integrativo = self.calculate_trattamento_integrativo(imponibile_irpef, irpef_lorda, detrazioni_spett)
        irpef_netta = self.calculate_irpef_netta(irpef_lorda, detrazioni_spett, imponibile_irpef)
   

        # Final Salary Calculation
        if self.ral <= 8174:
            stipendio_netto_euro = self.ral - inps_dip
        else:
            stipendio_netto_euro = self.ral - inps_dip - irpef_netta  + trattamento_integrativo

        costo_azienda_euro = self.ral + inps_azienda + tfr + inail
        stipendio_netto_gelato = stipendio_netto_euro / 3.2
        costo_azienda_gelato = costo_azienda_euro / 3.2

        result = {
        "RAL": self.ral,
        "INPS Dipendente": inps_dip,
        "IRPEF netta": irpef_netta,
        "IRPEF": irpef_lorda,
        "Addizionale Regionale": addizionale_regionale,
        "Addizionale Comunale": addizionale_comunale,
        "Detrazione spettante": detrazioni_spett,
        "Detrazione L207": self.calculate_detrazione_L207_2024(imponibile_irpef),
        "Trattamento integrativo": trattamento_integrativo,
        "INPS Azienda": inps_azienda,
        "TFR": tfr,
        "INAIL": inail,
        "Stipendio netto [Euro]": stipendio_netto_euro,
        "Costo azienda [Euro]": costo_azienda_euro,
        "Stipendio netto [Gelato]": stipendio_netto_gelato,
        "Costo azienda [Gelato]": costo_azienda_gelato
    }

        print("✅ Final Calculation Result:", result)  # Debug print
        return result  # ✅ Ensure this is inside the function

        

