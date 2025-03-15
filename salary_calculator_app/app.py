from flask import Flask, render_template, request, jsonify
from calculator import SalaryCalculator  # Ensure this matches your actual file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Debug: Print received data
        print("Received Data:", request.form)

        # Extract values from form
        ral = request.form.get('ral', '').strip()
        contract_type = request.form.get('contract_type', '').strip()
        agevolazioni = request.form.get('agevolazioni', '').strip()
        detrazioni = request.form.get('detrazioni', '').strip()
        ccnl_sector = request.form.get('ccnl_sector', '').strip()

        # Check if all required fields are provided
        if not all([ral, contract_type, agevolazioni, detrazioni, ccnl_sector]):
            print("❌ Missing Form Data:", {"ral": ral, "contract_type": contract_type, "agevolazioni": agevolazioni, "detrazioni": detrazioni, "ccnl_sector": ccnl_sector})
            return jsonify({"error": "Missing form data"}), 400

        # Convert RAL to float safely
        try:
            ral = float(ral)
        except ValueError:
            print("❌ Invalid RAL value:", ral)
            return jsonify({"error": f"Invalid RAL value: {ral}"}), 400

        # Initialize calculator and compute salary details
        calculator = SalaryCalculator(ral, contract_type, agevolazioni, detrazioni, ccnl_sector)
        result = calculator.calculate_stipendio_netto()

        # Debugging print (this shows all breakdown fields in terminal)
        print("✅ Calculation Result:", result)

        # Calculate monthly values based on the annual summary
        stipendio_netto_12 = result['Stipendio netto [Euro]'] / 12
        stipendio_netto_13 = result['Stipendio netto [Euro]'] / 13
        stipendio_netto_14 = result['Stipendio netto [Euro]'] / 14

        # Build a JSON response that includes both detailed breakdown and summary fields.
        # Note: All numbers are formatted to two decimals.
        formatted_result = {
            # Detailed Breakdown Fields (always in Euro)
            "RAL": f"{result.get('RAL', 0):.2f} €",
            "INPS Dipendente": f"{result.get('INPS Dipendente', 0):.2f} €",
            "IRPEF netta": f"{result.get('IRPEF netta', 0):.2f} €",
            "IRPEF": f"{result.get('IRPEF', 0):.2f} €",
            "Addizionale Regionale": f"{result.get('Addizionale Regionale', 0):.2f} €",
            "Addizionale Comunale": f"{result.get('Addizionale Comunale', 0):.2f} €",
            "Detrazione spettante": f"{result.get('Detrazione spettante', 0):.2f} €",
            "Detrazione L207": f"{result.get('Detrazione L207', 0):.2f} €",
            "Trattamento integrativo": f"{result.get('Trattamento integrativo', 0):.2f} €",
            "INPS Azienda": f"{result.get('INPS Azienda', 0):.2f} €",
            "TFR": f"{result.get('TFR', 0):.2f} €",
            "INAIL": f"{result.get('INAIL', 0):.2f} €",

            # Summary Fields (for toggle; these are used for both summary and monthly calculations)
            "Stipendio netto [Euro]": f"{result.get('Stipendio netto [Euro]', 0):.2f} €",
            "Costo azienda [Euro]": f"{result.get('Costo azienda [Euro]', 0):.2f} €",
            "Stipendio netto [Gelato]": f"{result.get('Stipendio netto [Euro]', 0) / 3.2:.2f} 🍦",
            "Costo azienda [Gelato]": f"{result.get('Costo azienda [Euro]', 0) / 3.2:.2f} 🍦",
            "Stipendio netto (12 mesi)": f"{stipendio_netto_12:.2f} €",
            "Stipendio netto (13 mesi)": f"{stipendio_netto_13:.2f} €",
            "Stipendio netto (14 mesi)": f"{stipendio_netto_14:.2f} €"
        }

        return jsonify(formatted_result)  # Return proper JSON

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
