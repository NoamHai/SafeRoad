const i18n = {
  en: {
    choose_language: "Choose a language",
    title: "Safe Roads",
    subtitle: "Accident Severity Classification",
    driving_conditions: "Accident Conditions",
    select_conditions: "Describe an accident scenario to classify its severity.",
    section_time_location: "Time & Location",
    section_road_conditions: "Road Conditions",
    section_accident_details: "Accident Details",
    label_SHAA: "Time",
    label_HODESH_TEUNA: "Month",
    label_YOM_BASHAVUA: "Day of Week",
    label_ZURAT_ISHUV: "Settlement Form",
    label_NAFA: "District",
    label_ROAD_STRUCTURE: "Road Structure",
    label_ROHAV: "Road Width",
    label_MEHIRUT_MUTERET: "Speed Limit",
    label_TEURA: "Lighting",
    label_SUG_DEREH: "Road Type",
    label_PNE_KVISH: "Road Surface",
    label_TKINUT: "Road Condition",
    label_MEZEG_AVIR: "Weather",
    label_YOM_LAYLA: "Day / Night",
    label_SUG_TEUNA: "Accident Type",
    label_SIMUN_TIMRUR: "Traffic Marking",
    predict_risk: "Classify Severity",
    analyzing: "Analyzing...",
    risk_assessment: "Severity Classification",
    risk_level: "Prediction",
    ready: "Ready",
    low_risk: "Lower probability",
    medium_risk_label: "Medium probability",
    high_risk: "Higher probability",
    light_accident: "Light Accident",
    dangerous_accident: "Dangerous Accident",
    recommendation: "Interpretation",
    risk_factors: "Prediction Details",
    select_conditions_advice: "Describe an accident scenario and click \"Classify Severity\". The result estimates severity, not whether an accident will occur.",
    calculating: "Calculating prediction...",
    why_this_risk: "Model output",
    low_risk_label: "Lower dangerous-class probability",
    high_risk_label: "Higher dangerous-class probability",
    low: "Low",
    medium: "Medium",
    high: "High",
    error: "Error",
    low_risk_advice: "Lower model probability of a dangerous accident, given the selected accident scenario. This does not estimate accident occurrence.",
    medium_risk_advice: "Medium model probability of a dangerous accident, given the selected accident scenario. This does not estimate accident occurrence.",
    high_risk_advice: "Higher model probability of a dangerous accident, given the selected accident scenario. This does not estimate accident occurrence.",
    unable_calculate: "Unable to Classify Severity",
    check_connection: "Please check your connection and try again.",
    footer_note: "Educational severity classifier. Dangerous means fatal or severe; the output is not the probability of an accident occurring.",
    network_error: "Network connection failed. Please check if the backend server is running.",
    server_error: "Server error occurred. Please try again later.",
    invalid_response: "Received invalid response from server.",
    factor_hour: "Hour",
    factor_month: "Month",
    factor_accident_type: "Accident Type",
    factor_speed_limit: "Speed Limit",
    factor_district: "District",
    validation_required_title: "Please complete all required fields",
    validation_required_message: "Missing fields: {fields}"
  },
  he: {
    choose_language: "בחר שפה",
    title: "כבישים בטוחים",
    subtitle: "סיווג חומרת תאונה",
    driving_conditions: "תנאי התאונה",
    select_conditions: "בחר מאפיינים של תרחיש תאונה כדי לסווג את חומרתה.",
    section_time_location: "זמן ומיקום",
    section_road_conditions: "תנאי הדרך",
    section_accident_details: "פרטי התאונה",
    label_SHAA: "זמן",
    label_HODESH_TEUNA: "חודש",
    label_YOM_BASHAVUA: "יום בשבוע",
    label_ZURAT_ISHUV: "צורת יישוב",
    label_NAFA: "נפה",
    label_ROAD_STRUCTURE: "מבנה הדרך",
    label_ROHAV: "רוחב כביש",
    label_MEHIRUT_MUTERET: "מהירות מותרת",
    label_TEURA: "תאורה",
    label_SUG_DEREH: "סוג דרך",
    label_PNE_KVISH: "מצב פני הכביש",
    label_TKINUT: "תקינות הדרך",
    label_MEZEG_AVIR: "מזג אוויר",
    label_YOM_LAYLA: "יום / לילה",
    label_SUG_TEUNA: "סוג תאונה",
    label_SIMUN_TIMRUR: "סימון תנועה",
    predict_risk: "סווג חומרה",
    analyzing: "מחשב...",
    risk_assessment: "סיווג חומרת תאונה",
    risk_level: "חיזוי",
    ready: "מוכן",
    low_risk: "הסתברות נמוכה יותר",
    medium_risk_label: "הסתברות בינונית",
    high_risk: "הסתברות גבוהה יותר",
    light_accident: "תאונה קלה",
    dangerous_accident: "תאונה מסוכנת",
    recommendation: "פירוש התוצאה",
    risk_factors: "פרטי החיזוי",
    select_conditions_advice: "בחר תרחיש תאונה ולחץ על \"סווג חומרה\". התוצאה מעריכה חומרה, ולא את הסיכוי שתתרחש תאונה.",
    calculating: "מחשב הערכה...",
    why_this_risk: "פלט המודל",
    low_risk_label: "הסתברות נמוכה יותר",
    high_risk_label: "הסתברות גבוהה יותר",
    low: "נמוך",
    medium: "בינוני",
    high: "גבוה",
    error: "שגיאה",
    low_risk_advice: "הסתברות מודל נמוכה יותר לתאונה מסוכנת, בהינתן תרחיש התאונה שנבחר. זו אינה הסתברות להתרחשות תאונה.",
    medium_risk_advice: "הסתברות מודל בינונית לתאונה מסוכנת, בהינתן תרחיש התאונה שנבחר. זו אינה הסתברות להתרחשות תאונה.",
    high_risk_advice: "הסתברות מודל גבוהה יותר לתאונה מסוכנת, בהינתן תרחיש התאונה שנבחר. זו אינה הסתברות להתרחשות תאונה.",
    unable_calculate: "לא ניתן לסווג חומרה",
    check_connection: "אנא בדוק את החיבור ונסה שוב.",
    footer_note: "הדגמה לימודית לסיווג חומרה. תאונה מסוכנת היא קטלנית או קשה; הפלט אינו הסיכוי שתתרחש תאונה.",
    network_error: "חיבור הרשת נכשל. בדוק אם שרת ה-backend פועל.",
    server_error: "אירעה שגיאת שרת. נסה שוב מאוחר יותר.",
    invalid_response: "התקבלה תגובה לא תקינה מהשרת.",
    factor_hour: "שעה",
    factor_month: "חודש",
    factor_accident_type: "סוג תאונה",
    factor_speed_limit: "מהירות מותרת",
    factor_district: "מחוז",
    validation_required_title: "אנא מלא/י את כל השדות הנדרשים",
    validation_required_message: "שדות חסרים: {fields}"
  }
};

/** Build the 24 hour choices with shared display labels. */
function buildHourOptions() {
  const rows = [];
  for (let hour = 0; hour <= 23; hour += 1) {
    const label = String(hour).padStart(2, "0");
    rows.push({ value: String(hour), en: label, he: label });
  }
  return rows;
}

/** Return the four quarter-hour choices accepted by the model. */
function buildMinuteOptions() {
  return [
    { value: "00", en: "00", he: "00" },
    { value: "15", en: "15", he: "15" },
    { value: "30", en: "30", he: "30" },
    { value: "45", en: "45", he: "45" }
  ];
}

/** Attach English and Hebrew labels to stable option keys. */
function buildLabeledOptions(entries) {
  return entries.map(([value, en, he]) => ({ value, en, he }));
}

/** Return month keys with bilingual labels. */
function buildMonthOptions() {
  return buildLabeledOptions([
    ["january", "January", "ינואר"],
    ["february", "February", "פברואר"],
    ["march", "March", "מרץ"],
    ["april", "April", "אפריל"],
    ["may", "May", "מאי"],
    ["june", "June", "יוני"],
    ["july", "July", "יולי"],
    ["august", "August", "אוגוסט"],
    ["september", "September", "ספטמבר"],
    ["october", "October", "אוקטובר"],
    ["november", "November", "נובמבר"],
    ["december", "December", "דצמבר"]
  ]);
}

const selectOptions = {
  SHAA_HOUR: buildHourOptions(),
  SHAA_MINUTE: buildMinuteOptions(),
  HODESH_TEUNA: buildMonthOptions(),
  YOM_BASHAVUA: buildLabeledOptions([
    ["sunday", "Sunday", "ראשון"],
    ["monday", "Monday", "שני"],
    ["tuesday", "Tuesday", "שלישי"],
    ["wednesday", "Wednesday", "רביעי"],
    ["thursday", "Thursday", "חמישי"],
    ["friday", "Friday", "שישי"],
    ["saturday", "Saturday", "שבת"]
  ]),
  SUG_TEUNA: buildLabeledOptions([
    ["pedestrian_collision", "Pedestrian collision", "פגיעה בהולך רגל"],
    ["front_to_side_collision", "Front to side collision", "התנגשות חזית אל צד"],
    ["front_to_rear_collision", "Front to rear collision", "התנגשות חזית באחור"],
    ["side_to_side_collision", "Side to side collision", "התנגשות צד בצד"],
    ["head_on_collision", "Head-on collision", "התנגשות חזית אל חזית"],
    ["collision_with_stopped_vehicle_not_parked", "Collision with stopped vehicle", "התנגשות עם רכב שנעצר ללא חניה"],
    ["collision_with_parked_vehicle", "Collision with parked vehicle", "התנגשות עם רכב חונה"],
    ["collision_with_stationary_object", "Collision with stationary object", "התנגשות עם עצם דומם"],
    ["leaving_or_entering_road", "Leaving or entering road", "ירידה מהכביש או עליה"],
    ["rollover", "Rollover", "התהפכות"],
    ["skidding", "Skidding", "החלקה"],
    ["passenger_injury_inside_vehicle", "Passenger injury inside vehicle", "פגיעה בנוסע בתוך כלי רכב"],
    ["fall_in_moving_vehicle", "Fall in moving vehicle", "נפילה ברכב נע"],
    ["fire", "Fire", "שריפה"],
    ["other", "Other", "אחר"],
    ["rear_to_front_collision", "Rear to front collision", "התנגשות אחור אל חזית"],
    ["rear_to_side_collision", "Rear to side collision", "התנגשות אחור אל צד"],
    ["collision_with_animal", "Collision with animal", "התנגשות עם בעל חיים"],
    ["injury_from_vehicle_cargo", "Injury from vehicle cargo", "פגיעה ממטען של רכב"]
  ]),
  ROAD_STRUCTURE: buildLabeledOptions([
    ["single_lane_1", "Single-lane road", "כביש חד מסלולי"],
    ["single_lane_2", "Two-lane road with built median", "כביש דו מסלולי עם שטח הפרדה בנוי"],
    ["single_lane_3", "Two-lane road without built median", "כביש דו מסלולי ללא שטח הפרדה בנוי"],
    ["multi_lane_1", "Multi-lane road with marked median", "כביש רב מסלולי עם שטח הפרדה מסומן"],
    ["multi_lane_2", "Multi-lane road with barrier", "כביש רב מסלולי עם מעקה הפרדה"],
    ["multi_lane_3", "Multi-lane road without built median", "כביש רב מסלולי עם שטח הפרדה לא בנוי"],
    ["multi_lane_4", "Multi-lane road without median", "כביש רב מסלולי ללא שטח הפרדה"],
    ["other", "Other / Unknown", "אחר / לא ידוע"]
  ]),
  ROHAV: buildLabeledOptions([
    ["unknown_road_width", "Unknown", "לא ידוע"],
    ["up_to_5_meters", "Up to 5 meters", "עד 5 מטר"],
    ["5_to_7_meters", "5–7 meters", "5 עד 7"],
    ["7_to_10_5_meters", "7–10.5 meters", "7 עד 10.5"],
    ["10_5_to_14_meters", "10.5–14 meters", "10.5 עד 14"],
    ["more_than_14_meters", ">14 meters", "יותר מ-14"]
  ]),
  MEHIRUT_MUTERET: buildLabeledOptions([
    ["unknown_speed_limit", "Unknown", "לא ידוע"],
    ["up_to_50_kmh", "Up to 50 km/h", "עד 50 קמ\"ש"],
    ["60_kmh", "60 km/h", "60 קמ\"ש"],
    ["70_kmh", "70 km/h", "70 קמ\"ש"],
    ["80_kmh", "80 km/h", "80 קמ\"ש"],
    ["90_kmh", "90 km/h", "90 קמ\"ש"],
    ["100_kmh", "100 km/h", "100 קמ\"ש"],
    ["110_kmh", "110 km/h", "110 קמ\"ש"],
    ["120_kmh", "120 km/h", "120 קמ\"ש"]
  ]),
  TEURA: buildLabeledOptions([
    ["daylight", "Daylight", "אור יום רגיל"],
    ["limited_visibility_due_to_weather", "Limited visibility due to weather", "ראות מוגבלת עקב מזג אוויר"],
    ["night_with_working_lighting", "Night with working lighting", "לילה פעלה תאורה"],
    ["night_with_faulty_or_non_working_lighting", "Night with faulty or non-working lighting", "קיימת תאורה בלתי תקינה / לא פועלת"],
    ["night_without_lighting", "Night without lighting", "לילה לא קיימת תאורה"],
    ["night_unknown_lighting", "Night unknown lighting", "לילה לא ידוע"],
    ["night_with_working_lighting_and_limited_visibility", "Night, working lighting, limited visibility", "לילה תאורה תקינה עם ראות מוגבלת"],
    ["night_with_faulty_lighting_and_limited_visibility", "Night, faulty lighting, limited visibility", "לילה תאורה לא תקינה עם ראות מוגבלת"],
    ["night_without_lighting_and_limited_visibility", "Night, no lighting, limited visibility", "לילה ללא תאורה עם ראות מוגבלת"],
    ["twilight", "Twilight", "דמדומים"],
    ["unknown_daylight_conditions", "Unknown daylight conditions", "יום לא ידוע"]
  ]),
  SUG_DEREH: buildLabeledOptions([
    ["urban_intersection", "Urban intersection", "דרך עירונית בצומת"],
    ["urban_non_intersection", "Urban non-intersection", "דרך עירונית לא בצומת"],
    ["non_urban_intersection", "Non-urban intersection", "דרך לא עירונית בצומת"],
    ["non_urban_non_intersection", "Non-urban non-intersection", "דרך לא עירונית לא בצומת"]
  ]),
  SIMUN_TIMRUR: buildLabeledOptions([
    ["defective_or_missing_road_marking", "Defective or missing road marking", "סימון לקוי או חסר"],
    ["defective_or_missing_sign", "Defective or missing sign", "תמרור לקוי או חסר"],
    ["no_defect", "No defect", "אין ליקוי"],
    ["no_sign_required", "No sign required", "לא נדרש תמרור"],
    ["unknown", "Unknown", "לא ידוע"]
  ]),
  PNE_KVISH: buildLabeledOptions([
    ["dry", "Dry", "יבש"],
    ["wet", "Wet", "רטוב ממים"],
    ["covered_with_fuel", "Covered with fuel", "מרוח בחומר דלק"],
    ["muddy", "Muddy", "מכוסה בבוץ"],
    ["sand_or_gravel", "Sand or gravel", "חול או חצץ על הכביש"],
    ["other", "Other", "אחר"],
    ["unknown", "Unknown", "לא ידוע"]
  ]),
  TKINUT: buildLabeledOptions([
    ["unknown_road_condition", "Unknown", "לא ידוע"],
    ["no_defect", "No defect", "אין ליקוי"],
    ["poor_road_shoulders", "Poor road shoulders", "שוליים גרועים"],
    ["uneven_surface", "Uneven surface", "כביש משובש"],
    ["poor_road_shoulders_and_uneven_surface", "Poor shoulders & uneven surface", "שוליים גרועים וכביש משובש"]
  ]),
  MEZEG_AVIR: buildLabeledOptions([
    ["clear", "Clear", "בהיר"],
    ["rainy", "Rainy", "גשום"],
    ["hot_and_dry", "Hot and dry", "שרבי"],
    ["foggy", "Foggy", "ערפילי"],
    ["other", "Other", "אחר"],
    ["unknown", "Unknown", "לא ידוע"]
  ]),
  YOM_LAYLA: buildLabeledOptions([
    ["day", "Day", "יום"],
    ["night", "Night", "לילה"]
  ]),
  ZURAT_ISHUV: buildLabeledOptions([
    ["urban_refugee_camps", "Urban refugee camps", "מחנה פליטים עירוני"],
    ["jewish_city_500k_plus", "Jewish settlement 500000+", "יישוב יהודי 500000+"],
    ["jewish_city_200k_500k", "Jewish settlement 499999-200000", "יישוב יהודי 499999-200000"],
    ["jewish_city_100k_200k", "Jewish settlement 199999-100000", "יישוב יהודי 199999-100000"],
    ["jewish_city_50k_100k", "Jewish settlement 99999-50000", "יישוב יהודי 99999-50000"],
    ["jewish_city_20k_50k", "Jewish settlement 49999-20000", "יישוב יהודי 49999-20000"],
    ["jewish_city_10k_20k", "Jewish settlement 19999-10000", "יישוב יהודי 19999-10000"],
    ["jewish_city_5k_10k", "Jewish settlement 9999-5000", "יישוב יהודי 9999-5000"],
    ["jewish_city_2k_5k", "Jewish settlement 4999-2000", "יישוב יהודי 4999-2000"],
    ["non_jewish_city_50k_100k", "Non-Jewish settlement 99999-50000", "יישוב לא יהודי 99999-50000"],
    ["non_jewish_city_20k_50k", "Non-Jewish settlement 49999-20000", "יישוב לא יהודי 49999-20000"],
    ["non_jewish_city_10k_20k", "Non-Jewish settlement 19999-10000", "יישוב לא יהודי 19999-10000"],
    ["non_jewish_city_5k_10k", "Non-Jewish settlement 9999-5000", "יישוב לא יהודי 9999-5000"],
    ["non_jewish_city_2k_5k", "Non-Jewish settlement 4999-2000", "יישוב לא יהודי 4999-2000"],
    ["moshav", "Moshav", "מושב"],
    ["moshav_shitufi", "Cooperative moshav", "מושב שיתופי"],
    ["kibbutz", "Kibbutz", "קיבוץ"],
    ["jewish_institutional_settlement", "Jewish institutional settlement", "יישוב מוסדי יהודי"],
    ["other_jewish_rural_settlement", "Other Jewish rural settlement", "יישוב כפרי יהודי אחר"],
    ["community_settlement", "Community settlement", "יישוב קהילתי"],
    ["non_jewish_institutional_settlement", "Non-Jewish institutional settlement", "יישוב מוסדי לא יהודי"],
    ["other_non_jewish_rural_settlement", "Other non-Jewish rural settlement", "יישוב כפרי לא יהודי אחר"],
    ["bedouin_tribes", "Bedouin tribes", "שבט בדווי"],
    ["rural_settlement", "Rural settlement", "יישוב כפרי"],
    ["unclassified_place", "Unclassified place", "מקום אחר / לא מסווג"],
    ["employment_center", "Employment center", "מוקד תעסוקה"],
    ["other_kibbutz_area", "Other kibbutz area", "אזור קיבוצי אחר"],
    ["rural_refugee_camps", "Rural refugee camps", "מחנה פליטים כפרי"],
    ["not_applicable_non_urban", "Not applicable — non-urban road", "לא רלוונטי — דרך לא עירונית"]
  ]),
  NAFA: buildLabeledOptions([
    ["unknown", "Unknown", "לא ידוע"],
    ["jerusalem", "Jerusalem", "ירושלים"],
    ["zefat", "Zefat", "צפת"],
    ["kinneret", "Kinneret", "כנרת"],
    ["yizreel", "Yizreel", "יזרעאל"],
    ["akko", "Akko", "עכו"],
    ["golan", "Golan", "גולן"],
    ["haifa", "Haifa", "חיפה"],
    ["hadera", "Hadera", "חדרה"],
    ["hasharon", "HaSharon", "השרון"],
    ["petah_tikva", "Petah Tikva", "פתח תקווה"],
    ["ramla", "Ramla", "רמלה"],
    ["rehovot", "Rehovot", "רחובות"],
    ["tel_aviv", "Tel Aviv", "תל אביב"],
    ["ashkelon", "Ashkelon", "אשקלון"],
    ["beer_sheva", "Beer Sheva", "באר שבע"],
    ["jenin", "Jenin", "ג'נין"],
    ["nablus", "Nablus", "שכם"],
    ["tulkarm", "Tulkarm", "טול כרם"],
    ["ramallah", "Ramallah", "ראמאללה"],
    ["jordan_jericho", "Jordan (Jericho)", "ירדן (יריחו)"],
    ["bethlehem", "Bethlehem", "בית לחם"],
    ["hebron", "Hebron", "חברון"],
    ["rafah", "Rafah", "רפיח"],
    ["gaza", "Gaza", "עזה"],
    ["khan_yunis", "Khan Yunis", "חאן יונס"],
    ["jabalia", "Jabalia", "ג'אבליא"],
    ["deir_al_balah", "Deir al-Balah", "דיר אל-בלח"]
  ])
};

let lastProbability = null;
let lastPrediction = null;

/** Read the active language from the document. */
function getCurrentLanguage() {
  return document.documentElement.lang === "he" ? "he" : "en";
}

/** Use the same origin on port 8000 or the local backend otherwise. */
function getApiEndpoint() {
  const currentPort = window.location.port;
  const currentHost = window.location.hostname;
  if (currentPort === "8000") {
    return "/predict";
  }
  return `http://${currentHost}:8000/predict`;
}

/** Update translated text without changing option values. */
function applyI18nText(lang) {
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    if (i18n[lang][key]) {
      element.textContent = i18n[lang][key];
    }
  });
}

/** Render translated choices while preserving the selected value. */
function renderOptionsForSelect(selectId, lang) {
  const select = document.getElementById(selectId);
  const options = selectOptions[selectId];
  if (!select || !options) {
    return;
  }

  const currentValue = select.value;
  select.innerHTML = "";

  options.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    const englishText = String(item.en ?? "").split("/")[0].trim();
    const hebrewText = String(item.he ?? "").split("/").pop().trim();
    option.textContent = lang === "he" ? (hebrewText || englishText) : (englishText || hebrewText);
    select.appendChild(option);
  });

  const hasPrevious = options.some((item) => item.value === currentValue);
  if (hasPrevious) {
    select.value = currentValue;
  } else if (selectId === "HODESH_TEUNA") {
    select.value = String(new Date().getMonth() + 1);
  } else if (selectId === "SHAA_HOUR") {
    select.value = String(new Date().getHours());
  } else if (selectId === "SHAA_MINUTE") {
    const currentMinute = new Date().getMinutes();
    const roundedMinute = String(Math.floor(currentMinute / 15) * 15).padStart(2, "0");
    select.value = roundedMinute;
  }
}

/** Refresh every select control for the chosen language. */
function renderAllSelectOptions(lang) {
  Object.keys(selectOptions).forEach((selectId) => renderOptionsForSelect(selectId, lang));
  updateSelectVisualState();
}

/** Mark controls that have a selected value. */
function updateSelectVisualState() {
  document.querySelectorAll(".input-group select").forEach((select) => {
    const hasValue = String(select.value || "").trim() !== "";
    select.classList.toggle("is-selected", hasValue);
  });
}

/** Choose a display band from the dangerous-class probability. */
function classifyRisk(probability) {
  const lang = getCurrentLanguage();
  if (probability < 0.33) {
    return { label: i18n[lang].low_risk_label, badge: i18n[lang].low, cssClass: "risk-low", color: "#2e7d32" };
  }
  if (probability < 0.66) {
    return { label: i18n[lang].medium_risk_label, badge: i18n[lang].medium, cssClass: "risk-medium", color: "#ed6c02" };
  }
  return { label: i18n[lang].high_risk_label, badge: i18n[lang].high, cssClass: "risk-high", color: "#d32f2f" };
}

/** Explain the current probability band without estimating accident occurrence. */
function setAdvice(probability) {
  const lang = getCurrentLanguage();
  if (probability < 0.33) {
    return i18n[lang].low_risk_advice;
  }
  if (probability < 0.66) {
    return i18n[lang].medium_risk_advice;
  }
  return i18n[lang].high_risk_advice;
}

/** Display the predicted class and both model probabilities. */
function renderPredictionSummary(prediction, lightProbability, dangerousProbability) {
  const explainDiv = document.getElementById("explain");
  if (!explainDiv) {
    return;
  }

  const lang = getCurrentLanguage();
  const predictionLabel = prediction === 1 ? i18n[lang].dangerous_accident : i18n[lang].light_accident;
  const predictionClass = lang === "he" ? "סיווג תאונה" : "Accident Classification";

  explainDiv.innerHTML = `
    <div class="risk-factors-title">${i18n[lang].why_this_risk}</div>
    <div class="risk-factors-list">
      <div class="risk-factor-item">
        <div class="factor-label">${predictionClass}</div>
        <div class="factor-value">${predictionLabel}</div>
        <div class="factor-impact positive">${prediction}</div>
      </div>
      <div class="risk-factor-item">
        <div class="factor-label">${lang === "he" ? "תאונה קלה" : "Light accident"}</div>
        <div class="factor-value">${Math.round(lightProbability * 100)}%</div>
        <div class="factor-impact positive">${Math.round(lightProbability * 100)}%</div>
      </div>
      <div class="risk-factor-item">
        <div class="factor-label">${lang === "he" ? "תאונה מסוכנת" : "Dangerous accident"}</div>
        <div class="factor-value">${Math.round(dangerousProbability * 100)}%</div>
        <div class="factor-impact negative">${Math.round(dangerousProbability * 100)}%</div>
      </div>
    </div>
  `;
}

/** Apply the probability band colors to the result panel. */
function applyRiskTheme(probability) {
  const resultSection = document.querySelector(".result-section");
  const explainDiv = document.getElementById("explain");
  if (!resultSection || !explainDiv) {
    return;
  }

  resultSection.classList.remove("risk-theme-low", "risk-theme-medium", "risk-theme-high");
  explainDiv.classList.remove("risk-factors--low", "risk-factors--medium", "risk-factors--high");

  if (probability < 0.33) {
    resultSection.classList.add("risk-theme-low");
    explainDiv.classList.add("risk-factors--low");
    return;
  }

  if (probability < 0.66) {
    resultSection.classList.add("risk-theme-medium");
    explainDiv.classList.add("risk-factors--medium");
    return;
  }

  resultSection.classList.add("risk-theme-high");
  explainDiv.classList.add("risk-factors--high");
}

/** Switch direction and labels while preserving inputs and the last result. */
function setLanguage(lang) {
  if (!i18n[lang]) {
    return;
  }

  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "he" ? "rtl" : "ltr";
  applyI18nText(lang);
  renderAllSelectOptions(lang);

  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
  });

  const advice = document.getElementById("advice");
  if (advice) {
    advice.textContent = lastProbability === null ? i18n[lang].select_conditions_advice : setAdvice(lastProbability);
  }

  if (lastProbability !== null) {
    const cls = classifyRisk(lastProbability);
    const percent = Math.round(lastProbability * 100);
    const riskText = document.getElementById("riskText");
    const riskBadge = document.getElementById("riskBadge");
    if (riskText) {
      riskText.textContent = lastPrediction === 1 ? i18n[lang].dangerous_accident : i18n[lang].light_accident;
      riskText.style.color = cls.color;
    }
    if (riskBadge) {
      riskBadge.textContent = cls.badge;
      riskBadge.className = `risk-badge ${cls.cssClass}`;
    }
    const lightProb = document.getElementById("lightProb");
    const dangerousProb = document.getElementById("dangerousProb");
    if (lightProb) {
      lightProb.textContent = `${Math.max(0, 100 - percent)}%`;
    }
    if (dangerousProb) {
      dangerousProb.textContent = `${percent}%`;
    }
    renderPredictionSummary(lastPrediction === null ? (percent >= 50 ? 1 : 0) : lastPrediction, Math.max(0, 1 - lastProbability), lastProbability);
  }

  localStorage.setItem("ui_language", lang);
}

/** Restore the saved language, defaulting to English. */
function initializeLanguage() {
  const saved = localStorage.getItem("ui_language");
  setLanguage(saved === "he" ? "he" : "en");
}

/** Read a selected option key or return the supplied default. */
function getStringValue(id, fallback) {
  const node = document.getElementById(id);
  if (!node) {
    return fallback;
  }
  const value = String(node.value || "").trim();
  return value === "" ? fallback : value;
}

/** Combine hour and minute selections into HH:MM. */
function getTimeValue(fallback) {
  const hour = getStringValue("SHAA_HOUR", "");
  const minute = getStringValue("SHAA_MINUTE", "");
  if (!hour || !minute) {
    return fallback;
  }
  return `${hour.padStart(2, "0")}:${minute.padStart(2, "0")}`;
}

/** Find a translated field label for validation messages. */
function getFieldLabel(id, lang) {
  if (id === "SHAA_HOUR") {
    return lang === "he" ? "שעה" : "Hour";
  }
  if (id === "SHAA_MINUTE") {
    return lang === "he" ? "דקות" : "Minutes";
  }
  const labelNode = document.querySelector(`label[for="${id}"]`);
  if (labelNode && labelNode.textContent.trim()) {
    return labelNode.textContent.trim();
  }
  return i18n[lang][`label_${id}`] || id;
}

/** Report empty controls before submitting the request. */
function validateRequiredFields() {
  const lang = getCurrentLanguage();
  const missingFields = [];

  Object.keys(selectOptions).forEach((id) => {
    const node = document.getElementById(id);
    if (!node || String(node.value || "").trim() === "") {
      missingFields.push(getFieldLabel(id, lang));
    }
  });

  if (missingFields.length === 0) {
    return { valid: true, message: "" };
  }

  return {
    valid: false,
    message: i18n[lang].validation_required_message.replace("{fields}", missingFields.join(", "))
  };
}

/** Display the missing-field explanation in the alert and result panel. */
function showValidationError(message) {
  const lang = getCurrentLanguage();
  const errorText = document.getElementById("errorText");
  const errorTitle = errorText ? errorText.querySelector("h3") : null;
  const errorBody = errorText ? errorText.querySelector("p") : null;
  const advice = document.getElementById("advice");

  if (errorText) {
    errorText.style.display = "block";
  }
  if (errorTitle) {
    errorTitle.textContent = i18n[lang].validation_required_title;
  }
  if (errorBody) {
    errorBody.textContent = message;
  }
  if (advice) {
    advice.textContent = message;
  }
}

/** Validate the form, request a prediction, and display the result or error. */
async function predict() {
  const lang = getCurrentLanguage();
  const btn = document.getElementById("btn");
  const btnText = document.querySelector(".btn-text");
  const btnLoading = document.querySelector(".btn-loading");
  const riskText = document.getElementById("riskText");
  const riskBadge = document.getElementById("riskBadge");
  const advice = document.getElementById("advice");
  const explainDiv = document.getElementById("explain");
  const errorText = document.getElementById("errorText");
  const gaugeNeedle = document.getElementById("gaugeNeedle");
  const lightProb = document.getElementById("lightProb");
  const dangerousProb = document.getElementById("dangerousProb");

  if (!btn || !btnText || !btnLoading || !riskText || !riskBadge || !advice || !explainDiv || !errorText || !gaugeNeedle || !lightProb || !dangerousProb) {
    return;
  }

  errorText.style.display = "none";
  btn.disabled = true;
  btnText.style.display = "none";
  btnLoading.style.display = "inline";

  const validation = validateRequiredFields();
  if (!validation.valid) {
    showValidationError(validation.message);
    btn.disabled = false;
    btnText.style.display = "inline";
    btnLoading.style.display = "none";
    return;
  }

  riskText.textContent = "...";
  riskText.style.color = "";
  riskBadge.textContent = i18n[lang].ready;
  riskBadge.className = "risk-badge";
  advice.textContent = i18n[lang].calculating;
  explainDiv.textContent = "";

  const payload = {
    SHAA: getTimeValue("00:00"),
    HODESH_TEUNA: getStringValue("HODESH_TEUNA", "1"),
    YOM_BASHAVUA: getStringValue("YOM_BASHAVUA", "לא ידוע"),
    SUG_TEUNA: getStringValue("SUG_TEUNA", "לא ידוע"),
    ROAD_STRUCTURE: getStringValue("ROAD_STRUCTURE", "לא ידוע"),
    ROHAV: getStringValue("ROHAV", "לא ידוע"),
    NAFA: getStringValue("NAFA", "לא ידוע"),
    ZURAT_ISHUV: getStringValue("ZURAT_ISHUV", "לא ידוע"),
    MEHIRUT_MUTERET: getStringValue("MEHIRUT_MUTERET", "לא ידוע"),
    TEURA: getStringValue("TEURA", "לא ידוע"),
    SUG_DEREH: getStringValue("SUG_DEREH", "לא ידוע"),
    SIMUN_TIMRUR: getStringValue("SIMUN_TIMRUR", "לא ידוע"),
    TKINUT: getStringValue("TKINUT", "לא ידוע"),
    PNE_KVISH: getStringValue("PNE_KVISH", "לא ידוע"),
    MEZEG_AVIR: getStringValue("MEZEG_AVIR", "לא ידוע"),
    YOM_LAYLA: getStringValue("YOM_LAYLA", "לא ידוע")
  };

  try {
    const response = await fetch(getApiEndpoint(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const prediction = Number(data.prediction);
    const dangerousProbability = Number(data.dangerous_probability);
    const lightProbability = Number(data.light_probability);

    if (![0, 1].includes(prediction) || !Number.isFinite(dangerousProbability) || !Number.isFinite(lightProbability)) {
      throw new Error("invalid_probability");
    }

    const percent = Math.round(dangerousProbability * 100);
    const cls = classifyRisk(dangerousProbability);

    lastProbability = dangerousProbability;
    lastPrediction = prediction;

    riskText.textContent = prediction === 1 ? i18n[lang].dangerous_accident : i18n[lang].light_accident;
    riskText.style.color = cls.color;
    // The badge and gauge use the same display bands for dangerous-class probability.
    riskBadge.textContent = cls.badge;
    riskBadge.className = `risk-badge ${cls.cssClass}`;
    advice.textContent = setAdvice(dangerousProbability);

    gaugeNeedle.style.left = `${Math.max(0, Math.min(100, percent))}%`;
    dangerousProb.textContent = `${Math.max(0, Math.min(100, Math.round(dangerousProbability * 100)))}%`;
    lightProb.textContent = `${Math.max(0, Math.min(100, Math.round(lightProbability * 100)))}%`;

    renderPredictionSummary(prediction, lightProbability, dangerousProbability);
    applyRiskTheme(dangerousProbability);
  } catch (error) {
    let userMessage = i18n[lang].server_error;
    if (error instanceof TypeError) {
      userMessage = i18n[lang].network_error;
    } else if (String(error.message).includes("invalid_probability")) {
      userMessage = i18n[lang].invalid_response;
    }

    errorText.querySelector("h3").textContent = i18n[lang].unable_calculate;
    errorText.querySelector("p").textContent = userMessage;
    errorText.style.display = "block";
    advice.textContent = userMessage;
    riskBadge.textContent = i18n[lang].error;
    riskBadge.className = "risk-badge risk-error";
  } finally {
    btn.disabled = false;
    btnText.style.display = "inline";
    btnLoading.style.display = "none";
  }
}

/** Connect language, prediction, and select-change handlers. */
function bindEvents() {
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const lang = btn.getAttribute("data-lang") === "he" ? "he" : "en";
      setLanguage(lang);
    });
  });

  const predictButton = document.getElementById("btn");
  if (predictButton) {
    predictButton.addEventListener("click", (event) => {
      event.preventDefault();
      predict();
    });
  }

  document.querySelectorAll(".input-group select").forEach((select) => {
    select.addEventListener("change", updateSelectVisualState);
  });
}

/** Initialize controls, language, events, and empty result values. */
function initializeApp() {
  initializeLanguage();
  renderAllSelectOptions(getCurrentLanguage());
  bindEvents();

  document.querySelectorAll(".input-group select").forEach((select) => {
    select.required = true;
    select.setAttribute("aria-required", "true");
  });

  const advice = document.getElementById("advice");
  if (advice) {
    advice.textContent = i18n[getCurrentLanguage()].select_conditions_advice;
  }

  const gaugeNeedle = document.getElementById("gaugeNeedle");
  if (gaugeNeedle) {
    gaugeNeedle.style.left = "0%";
  }

  const lightProb = document.getElementById("lightProb");
  const dangerousProb = document.getElementById("dangerousProb");
  if (lightProb) {
    lightProb.textContent = "--%";
  }
  if (dangerousProb) {
    dangerousProb.textContent = "--%";
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp);
} else {
  initializeApp();
}
