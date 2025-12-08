# Smart Money Concept (TradingFinder) – Pine to Python Mapping

## القسم 1 – خريطة منطق المؤشر (Pine Script)

### 1.1 معلومات عامة
- اسم المؤشر: `Smart Money Concept [TradingFinder] Major Minor OB + FVG (SMC)` كما هو في `indicator` السطر الأول.【F:111111.txt†L4-L6】
- النسخة: `@version=5`.【F:111111.txt†L4-L6】
- إعدادات الماكس: `max_bars_back = 5000`, `max_boxes_count = 500`, `max_labels_count = 500`, `max_lines_count = 500`.【F:111111.txt†L4-L6】
- المكتبات المستوردة: Refiner (OrderBlockRefiner), Drawing (OrderBlockDrawing), FVG (FVGDetector), Liq (LiquidityFinder), Alert (AlertSender), TradingView/ta (تحليلات أساسية). الكود غير متوفر لذا تم توثيق الاستخدام فقط.【F:111111.txt†L8-L19】

### 1.2 جدول المدخلات (Inputs Table)
- Pivot Period (`PP`): int، افتراضي 5، مجموعة Logic Parameter، يحدد طول pivot لاكتشاف الـ Order Blocks.【F:111111.txt†L24-L25】
- Order Block Validity (`OBVaP`): int، افتراضي 500، مجموعة Logic Parameter، فترة صلاحية المناطق بالشموع.【F:111111.txt†L24-L27】
- ShowDmainCh/ColorDmainCh: bool+color، عرض مناطق الطلب الرئيسية (ChoCh Origin).【F:111111.txt†L29-L33】
- ShowDsubCh/ColorDsubCh: bool+color، عرض مناطق الطلب الفرعية (ChoCh Origin).【F:111111.txt†L36-L40】
- ShowDBoS/ColorDBoS: bool+color، عرض مناطق الطلب BoS Origin.【F:111111.txt†L43-L47】
- ShowSmainCh/ColorSmainCh: bool+color، عرض مناطق العرض الرئيسية ChoCh.【F:111111.txt†L50-L54】
- ShowSsubCh/ColorSsubCh: bool+color، عرض مناطق العرض الفرعية ChoCh.【F:111111.txt†L57-L61】
- ShowSBoS/ColorSBoS: bool+color، عرض مناطق العرض BoS.【F:111111.txt†L64-L68】
- RefineDmainCh/RefineMeDmainCh: bool+string، تفعيل/نمط Refinement لمناطق الطلب الرئيسية ChoCh.【F:111111.txt†L72-L80】
- RefineDsubCh/RefineMeDsubCh: bool+string، Refinement للطلب الفرعي ChoCh.【F:111111.txt†L83-L91】
- RefineDBoS/RefineMeDBoS: bool+string، Refinement لمناطق الطلب BoS Origin.【F:111111.txt†L94-L102】
- RefineSmainCh/RefineMeSmainCh: bool+string، Refinement لمناطق العرض الرئيسية ChoCh.【F:111111.txt†L105-L113】
- RefineSsubCh/RefineMeSsubCh: bool+string، Refinement للعرض الفرعي ChoCh.【F:111111.txt†L116-L124】
- RefineSBoS/RefineMeSBoS: bool+string، Refinement لمناطق العرض BoS.【F:111111.txt†L127-L135】
- FVG inputs: PShowDeFVG, PShowSuFVG (bool), PFVGFilter (bool), PFVGFilterType (string حساسية).【F:111111.txt†L141-L144】
- Liquidity inputs: ShowSHLL, ShowSLLL, ShowDHLL, ShowDLLL (bool)، SPP/DPP (int pivot)، SLLS/DLLS (float حساسية).【F:111111.txt†L152-L162】
- Alert inputs: AlertName, Alert_DMM/DSM/DAM/SMM/SSM/SAM (string On/Off)، رسائل النص MessageBull/Bear، Frequncy، UTC، MoreInfo.【F:111111.txt†L167-L199】
- Line display inputs: مجموعات BoS/ChoCh للـ Major/Minor ودعم/مقاومة الأخيرة، جميعها string لاختيار On/Off والستايل واللون.【F:111111.txt†L208-L286】

### 1.3 المتغيرات العامة والثابتة
- مصفوفات ZigZag: ArrayType, ArrayValue, ArrayIndex, ArrayTypeAdv, ArrayValueAdv, ArrayIndexAdv تستخدم لتتبع نوع pivot والقيم والفهارس.【F:111111.txt†L300-L333】
- Pivots: HighPivot, LowPivot, HighValue/Index, LowValue/Index تعتمد على PP وتستخدم كحجر أساس للهيكل.【F:111111.txt†L320-L333】
- مستويات Major/Minor: Major_HighLevel/LowLevel/Index/Type و Minor_HighLevel/LowLevel/Index/Type تخزن آخر قمم/قيعان رئيسية وفرعية.【F:111111.txt†L335-L347】
- متغيرات ChoCh/BoS لاحقاً تنتج الأعلام Bullish/Bearish للـ Major/Minor مع مؤشرات pivot مرتبطة (كما يظهر في نهاية الكود عبر BuMChMain_Index إلخ).【F:indicator.py†L1375-L1454】

### 1.4 البلوكات المنطقية الرئيسية
- اكتشاف الـ ZigZag والـ Pivots: يعتمد على ta.pivothigh/pivotlow مع PP ويملأ المصفوفات ArrayType/Value/Index لإيجاد آخر Pivot وأنواعه (mHH/mLL/MHH/MLL... إلخ).【F:111111.txt†L300-L333】
- مستويات Major/Minor: تحديث القيم Major/Minor بناءً على قوة الحركة ومستويات ATR (يُستخدم ATR=ta.atr(55)).【F:111111.txt†L317-L333】
- كشف ChoCh و BoS: يتم تحديد Bullish/Bearish Major/Minor ChoCh/BoS عبر مقارنة آخر pivots بالـ Major/Minor السابق وتحديد اتجاه الاختراق. النتائج تخزن في أعلام مثل `Bullish_Major_ChoCh`, `Bearish_Minor_BoS` وتتصل بمؤشرات pivots مثل `LastPivotIndex` و `LastPivotIndex02`.【F:indicator.py†L1296-L1373】
- رسم خطوط الدعم/المقاومة: يعتمد على الإعدادات LastMajor/Minor Support/Resistance Line ويستخدم line.new وفقاً للأعلام، لكنها رسومية فقط (غير منقولة للبايثون).【F:111111.txt†L265-L286】
- بناء مناطق الطلب/العرض: الأعلام BuMChMain_Trigger / BuMChSub_Trigger / BuMBoS_Trigger للطلب و BeMChMain_Trigger / BeMChSub_Trigger / BeMBoS_Trigger للعرض تُحسب من ChoCh/BoS، ثم تمر عبر Refiner.OBRefiner لتحديد Xd/Xp/Yd/Yp. التحسين يعتمد على إعدادات Refine*.【F:indicator.py†L1375-L1424】
- Refinement OB: عبر Refiner.OBRefiner لكل نوع منطقة يعيد حدود المنطقة (Xd1/Xd2/Yd12 إلخ). الكود غير متوفر وتم وضع Placeholder في بايثون.【F:indicator.py†L1375-L1391】
- FVG Filter: FVG.FVGDetector يُستدعى مع PFVGFilterType وإعدادات العرض لفلترة/إظهار مناطق FVG.【F:indicator.py†L1449-L1452】
- Liquidity: Liq.LLF يستخدم إعدادات SPP/DPP/SLLS/DLLS وفلاتر العرض. دوره احتمالاً رسم خطوط سيولة واستعمالها كفلتر بصري.【F:indicator.py†L1454-L1456】
- Alert Sender: Alert.AlertSender يُستدعى لكل من الست رسائل بناءً على Alert_D*** / Alert_S*** flags مع تمرير بيانات المنطقة (Yd12/Yp12).【F:indicator.py†L1460-L1469】

### 1.5 ربط الشروط والتنبيهات النصية
- "Long Position in Demand Main Zone ChoCh Origin." → Alert_DMMM flag يعتمد على BuMChMain_Trigger بعد مرور Refiner و Drawing مع إظهار المنطقة ShowDmainCh ومدة الصلاحية OBVaP؛ التنبيه يرسل فقط إذا Alert_DMM مدخَل المستخدم = "On".【F:indicator.py†L1375-L1463】
- "Long Position in Demand Sub Zone ChoCh Origin." → Alert_DSMM يعتمد على BuMChSub_Trigger، مع ShowDsubCh و Alert_DSM."【F:indicator.py†L1376-L1464】
- "Long Position in Demand Zone BoS Origin." → Alert_DAMM يعتمد على BuMBoS_Trigger، ShowDBoS و Alert_DAM."【F:indicator.py†L1377-L1464】
- "Short Position in Supply Main Zone ChoCh Origin." → Alert_SMMM يعتمد على BeMChMain_Trigger، ShowSmainCh و Alert_SMM."【F:indicator.py†L1380-L1467】
- "Short Position in Supply Sub Zone ChoCh Origin." → Alert_SSMM يعتمد على BeMChSub_Trigger، ShowSsubCh و Alert_SSM."【F:indicator.py†L1381-L1467】
- "Short Position in Supply Zone BoS Origin." → Alert_SAMM يعتمد على BeMBoS_Trigger، ShowSBoS و Alert_SAM."【F:indicator.py†L1382-L1469】

## القسم 2 – خريطة التحويل من Pine Script إلى Python

### 2.1 جدول Mapping الأسماء
- مدخلات Pine → متغيرات الإعداد في `smc_scanner.py` بنفس الأسماء (PP, OBVaP, ShowDmainCh ... Alert_SAM).【F:smc_scanner.py†L23-L89】
- أعلام التريغر (BuMChMain_Trigger إلخ) → حقول dict في evaluate_structure() و build_order_blocks().【F:smc_scanner.py†L115-L173】
- Refiner.OBRefiner → order_block_refiner() placeholder يمرر trigger/index فقط.【F:smc_scanner.py†L91-L105】
- Drawing.OBDrawing → ob_drawing() placeholder يعيد علم التفعيل.【F:smc_scanner.py†L108-L110】
- FVG.FVGDetector → fvg_detector() placeholder بدون منطق فعلي.【F:smc_scanner.py†L112-L119】
- Liq.LLF → liquidity_finder() placeholder.【F:smc_scanner.py†L121-L123】
- Alert.AlertSender → alert_sender() يطبع الرسائل النصية بنفس نص Pine عندما تتوفر الأعلام والإعدادات On.【F:smc_scanner.py†L175-L205】

### 2.2 اختلافات اللغة/البيئة
- Pine series (open/high/low/close) تُستبدل بقوائم OHLCV من ccxt (`[timestamp, open, high, low, close, volume]`). آخر شمعة مكتملة هي candles[-2].【F:smc_scanner.py†L184-L200】
- لا يوجد رسم رسومي في Python؛ خطوط BoS/ChoCh والدعم/المقاومة غير منفذة لأنها تعتمد على واجهة TradingView الرسومية.【F:smc_scanner.py†L23-L119】
- حلقة التنفيذ بينما True مع time.sleep بدلاً من تحديث شمعات تلقائي في Pine.【F:smc_scanner.py†L207-L227】

### 2.3 سياسة التطابق 1:1
- منطق Refiner/Drawing/FVG/Liquidity/AlertSender غير متاح في المصدر المستورد؛ تم استبداله بـ placeholders، لذا لا يمكن ضمان تطابق إشارات بنسبة 99.99% حتى يُعاد بناء المنطق المفقود.【F:smc_scanner.py†L91-L123】
- كشف ChoCh/BoS الحقيقي غير مفعل في evaluate_structure() (الأعلام False افتراضياً) لأنه يحتاج خوارزمية zigzag pivots الكاملة؛ يجب ملؤها لاحقاً لتطابق 1:1.【F:smc_scanner.py†L125-L142】
- عناصر الرسم (خطوط BoS/ChoCh والدعم/المقاومة) غير مدعومة في بيئة الطرفية لذا تم تجاهلها مع توثيق ذلك.【F:SMC_report.md†L11-L19】

## القسم 3 – سكربت Python كامل (جاهز للتشغيل)
انظر الملف `smc_scanner.py` في هذا المستودع. يعتمد على ccxt، حلقة while True، وإعدادات مطابقة للـ Pine قدر الإمكان مع placeholders للأجزاء المفقودة.【F:smc_scanner.py†L1-L228】

## القسم 4 – ملاحظات وحدود التحويل
- الأجزاء المنقولة 1:1: إعدادات المدخلات، أسماء الأعلام، رسائل التنبيه، وهيكل حلقة الفحص وإطلاق التنبيهات النصية.【F:smc_scanner.py†L23-L205】
- الأجزاء Placeholder: Refiner/OB drawing/FVG/Liquidity/AlertSender المنفذة كدوال فارغة، وكشف ChoCh/BoS لم يطبق بعد بسبب اعتماد شديد على كود Pine والمكتبات المغلقة.【F:smc_scanner.py†L91-L142】
- اختلافات بيئية: لا رسومات أو كائنات line/label في Python؛ الاعتماد على بيانات ccxt بدلاً من series المدمجة في TradingView.【F:smc_scanner.py†L23-L200】
