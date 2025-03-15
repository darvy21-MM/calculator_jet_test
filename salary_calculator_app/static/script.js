$(document).ready(function() {
    const RATE = 3.2; // Conversion factor for Gelato

    // -------------------------------
    // 1) SUMMARY (TOGGLE) VARIABLES
    // -------------------------------
    let stipendioAnnualeEuro = 0, stipendio12Euro = 0, stipendio13Euro = 0, stipendio14Euro = 0;
    let costoAnnualeEuro = 0;

    // The Gelato equivalents
    let stipendioAnnualeGelato = 0, stipendio12Gelato = 0, stipendio13Gelato = 0, stipendio14Gelato = 0;
    let costoAnnualeGelato = 0;

    // -------------------------------
    // 2) DETAILED BREAKDOWN (ALWAYS EURO)
    // -------------------------------
    let detail_RAL = 0;
    let detail_INPS_dip = 0;
    let detail_IRPEF_netta = 0;
    let detail_IRPEF = 0;
    let detail_Addizionale_regionale = 0;
    let detail_Addizionale_comunale = 0;
    let detail_Detrazioni_spett = 0;
    let detail_Detrazione_L207 = 0;
    let detail_Trattamento_integrativo = 0;

    let detail_INPS_azienda = 0;
    let detail_TFR = 0;
    let detail_INAIL = 0;

    // Helper to format numeric values to 2 decimals
    function formatValue(value) {
      return parseFloat(value).toFixed(2);
    }

    // --------------------------------------------
    // UPDATE SUMMARY DISPLAY (STIPENDIO + COSTO)
    // --------------------------------------------
    // This is where we handle the Euro ↔ Gelato toggle
    function updateSummaryDisplay() {
      const useGelato = $("#currency-toggle").is(":checked");

      if (useGelato) {
        $("#stipendioAnnuale").text(formatValue(stipendioAnnualeGelato) + " 🍦");
        $("#stipendio12").text(formatValue(stipendio12Gelato) + " 🍦");
        $("#stipendio13").text(formatValue(stipendio13Gelato) + " 🍦");
        $("#stipendio14").text(formatValue(stipendio14Gelato) + " 🍦");
        $("#costoAnnuale").text(formatValue(costoAnnualeGelato) + " 🍦");
      } else {
        $("#stipendioAnnuale").text(formatValue(stipendioAnnualeEuro) + " €");
        $("#stipendio12").text(formatValue(stipendio12Euro) + " €");
        $("#stipendio13").text(formatValue(stipendio13Euro) + " €");
        $("#stipendio14").text(formatValue(stipendio14Euro) + " €");
        $("#costoAnnuale").text(formatValue(costoAnnualeEuro) + " €");
      }
    }

    // -------------------------------------------------------
    // UPDATE DETAILED DISPLAY (RAL, INPS, IRPEF, etc. in EURO)
    // -------------------------------------------------------
    // Always Euro, no toggle
    function updateDetailedDisplay() {
      $("#detail-ral").text(formatValue(detail_RAL) + " €");
      $("#detail-inps-dip").text(formatValue(detail_INPS_dip) + " €");
      $("#detail-irpef-netta").text(formatValue(detail_IRPEF_netta) + " €");
      $("#detail-irpef").text(formatValue(detail_IRPEF) + " €");
      $("#detail-addizionale-regionale").text(formatValue(detail_Addizionale_regionale) + " €");
      $("#detail-addizionale-comunale").text(formatValue(detail_Addizionale_comunale) + " €");
      $("#detail-detrazioni-spett").text(formatValue(detail_Detrazioni_spett) + " €");
      $("#detail-detrazione-l207").text(formatValue(detail_Detrazione_L207) + " €");
      $("#detail-trattamento-integrativo").text(formatValue(detail_Trattamento_integrativo) + " €");

      $("#detail-ral-cost").text(formatValue(detail_RAL) + " €");
      $("#detail-inps-azienda").text(formatValue(detail_INPS_azienda) + " €");
      $("#detail-tfr").text(formatValue(detail_TFR) + " €");
      $("#detail-inail").text(formatValue(detail_INAIL) + " €");
    }

    // When toggle changes, update only the summary display
    $("#currency-toggle").change(function() {
      updateSummaryDisplay();
    });

    // ---------------------------------------------
    // CONTRACT SELECTION LOGIC (AS YOU ALREADY HAD)
    // ---------------------------------------------
    function handleContractSelection() {
      let selectedContract = $("#contract_type").val();
      if (selectedContract === "apprendistato" || selectedContract === "collaboratore") {
        $("#agevolazioni").val("nessuna agevolazione").prop("disabled", true);
      } else {
        $("#agevolazioni").prop("disabled", false);
      }

      if (selectedContract === "determinato") {
        $("#agevolazioni option[value='under 30'], #agevolazioni option[value='under 36']")
          .prop("disabled", true);
        if ($("#agevolazioni").val() === "under 30" || $("#agevolazioni").val() === "under 36") {
          $("#agevolazioni").val("nessuna agevolazione");
        }
      } else {
        $("#agevolazioni option[value='under 30'], #agevolazioni option[value='under 36']")
          .prop("disabled", false);
      }
    }

    $("#contract_type").change(function () {
      handleContractSelection();
    });
    handleContractSelection();

    // ---------------------------------------------
    // FORM SUBMISSION -> AJAX POST TO /calculate
    // ---------------------------------------------
    $("#salaryForm").submit(function(event) {
      event.preventDefault();
      $("#agevolazioni").prop("disabled", false);

      $.ajax({
        type: "POST",
        url: "/calculate",
        data: $(this).serialize(),
        success: function(response) {
          console.log("Server Response:", response);

          // 1) SUMMARY FIELDS (Euro)
          stipendioAnnualeEuro = parseFloat(response["Stipendio netto [Euro]"]) || 0;
          stipendio12Euro      = parseFloat(response["Stipendio netto (12 mesi)"]) || 0;
          stipendio13Euro      = parseFloat(response["Stipendio netto (13 mesi)"]) || 0;
          stipendio14Euro      = parseFloat(response["Stipendio netto (14 mesi)"]) || 0;
          costoAnnualeEuro     = parseFloat(response["Costo azienda [Euro]"]) || 0;

          // 2) SUMMARY FIELDS (Gelato) => Convert from Euro
          stipendioAnnualeGelato = stipendioAnnualeEuro / RATE;
          stipendio12Gelato      = stipendio12Euro / RATE;
          stipendio13Gelato      = stipendio13Euro / RATE;
          stipendio14Gelato      = stipendio14Euro / RATE;
          costoAnnualeGelato     = costoAnnualeEuro / RATE;

          // 3) DETAILED FIELDS (Always Euro)
          detail_RAL                   = parseFloat(response["RAL"]) || parseFloat($("#ral").val()) || 0;
          detail_INPS_dip             = parseFloat(response["INPS Dipendente"]) || 0;
          detail_IRPEF_netta          = parseFloat(response["IRPEF netta"]) || 0;
          detail_IRPEF                = parseFloat(response["IRPEF"]) || 0;
          detail_Addizionale_regionale= parseFloat(response["Addizionale Regionale"]) || 0;
          detail_Addizionale_comunale = parseFloat(response["Addizionale Comunale"]) || 0;
          detail_Detrazioni_spett     = parseFloat(response["Detrazione spettante"]) || 0;
          detail_Detrazione_L207      = parseFloat(response["Detrazione L207"]) || 0;
          detail_Trattamento_integrativo = parseFloat(response["Trattamento integrativo"]) || 0;

          detail_INPS_azienda         = parseFloat(response["INPS Azienda"]) || 0;
          detail_TFR                  = parseFloat(response["TFR"]) || 0;
          detail_INAIL                = parseFloat(response["INAIL"]) || 0;

          // Show the results container
          $("#resultsWrapper").show();

          // Update summary display (with toggle)
          updateSummaryDisplay();
          // Update detail display (always Euro)
          updateDetailedDisplay();
        },
        error: function(xhr, status, error) {
          console.error("AJAX Error:", status, error);
        }
      });

      handleContractSelection();
    });
});
