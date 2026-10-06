"""Build the decision-maker slide deck of the Nofit LRT extension demand study, in English and in Hebrew:
   reports/Nofit_LRT_Extension_Decision_Deck.html      -- English
   reports/Nofit_LRT_Extension_Decision_Deck_HE.html   -- Hebrew (right-to-left layout, same numbers and charts)
One self-contained HTML file each (keyboard / swipe navigation, inline SVG charts, the route map embedded).
Every number is taken from reports/Nofit_LRT_Extension_Comprehensive_Report.docx (built by tools/build_comprehensive_report.py);
the table or section it comes from is named beside each value below. The Hebrew wording follows the Hebrew report
(reports/Nofit_LRT_Extension_Comprehensive_Report_HE.docx). The narrative follows the storytelling-with-data structure:
lead with the answer, then the evidence, then the ask.
Run:  python3 tools/build_decision_deck.py                          -- both files
      python3 tools/build_decision_deck.py --lang he --body-only out.html   -- one language, without the html/head/body skeleton"""
import base64, io, os, sys
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
OUT_HTML = {'en': 'reports/Nofit_LRT_Extension_Decision_Deck.html', 'he': 'reports/Nofit_LRT_Extension_Decision_Deck_HE.html'}
MAP_PNG = 'Output/figures/lrt_alternatives_lines.png'

# ---------------- the numbers (reference case 2050 BU, main route + extension, Prioritized, AM 06:00-09:00 unless stated) ----------------
LRT_TOTAL = [5193, 6309, 7433, 7476, 9225]            # Table 4.3 (AM three hours), by scenario 2022 / 2040 BU / 2050 BU / 2040 HS / 2050 HS
LRT_EXT = [4004, 4950, 6003, 5651, 7010]              # Table 4.3, "LRT using the extension"
PEAK_LOAD = [840, 966, 1071, 1146, 1397]              # Table 4.2a, through line peak load on the line (AM peak hour, one direction)
MARKETS = [2189, 1663, 1665, 891, 522, 306, 193]      # Table 4.5 (labels in the strings table, same order)
SOURCES = [3731, 2881, 818]                           # Table 4.3, 2050 BU: from the Metronit, from buses, from cars
THROUGH = {'ext_only': (5939, 5939), 'through': (6003, 7433)}   # Table 4.1: (extension riders, total LRT riders)
REGIME = [6309, 7433, 5700]                           # Tables 4.3, 4.8: 2040 BU prioritized, 2050 BU prioritized, 2050 BU unprioritized
RANGE = {'low': 5532, 'central': 7433, 'high': 10537, 'unprioritized': 5700}   # Executive summary planning range

# ---------------- the words ----------------
S = {}
S['en'] = dict(
    lang='en', dir='ltr', title='Nofit Extension Decision Brief',
    fonts='https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Public+Sans:ital,wght@0,400;0,600;1,400&display=swap',
    display='"Archivo", "Helvetica Neue", Arial, sans-serif', body='"Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif',
    nav_title='Nofit light rail · extension through Haifa to Tirat Carmel', prev='‹ Prev', next='Next ›', prev_aria='Previous slide', next_aria='Next slide', slide_aria='Slide',
    scen=['2022', '2040 BU', '2050 BU', '2040 HS', '2050 HS'],
    cover_eyebrow='Decision brief · Nofit light rail · October 2026',
    cover_title='Should the Nofit light rail continue through Haifa to Tirat Carmel?',
    cover_lede='What the travel demand evidence says, in plain language. Prepared for decision makers from the comprehensive demand report of 5 October 2026.',
    cover_facts=[('Reference case', 'Year 2050, business-as-usual growth, trams with priority at road junctions'), ('Period', 'Morning peak, 06:00–09:00, unless stated'), ('Navigate', 'Arrow keys, space, or the buttons below')],
    s2_eyebrow='The short answer',
    s2_title='The extension has a real light-rail market. It needs priority at the junctions more than it needs a through service, and the numbers are ready for sizing the line, not yet for buying trains.',
    s2_tiles=[('7,400', 'people ride the whole line each morning peak in 2050'), ('4 in 5', 'of them use the extension through Haifa'), ('−23 %', 'riders lost if trams queue at junctions like cars')],
    s2_h_evidence='What the evidence says',
    s2_evidence=['The riders are in Haifa and Tirat Carmel, in three markets of similar size.', 'Most of them switch from the Metronit and buses. Few leave their cars.', 'Running through to Nazareth saves a change of vehicle; it does not add riders to the extension.'],
    s2_h_ask='What we ask you to decide',
    s2_ask=['Plan on the 2050 reference case, with 5,500 to 10,500 morning riders as the range.', 'Protect tram priority at the junctions in the design.', 'Settle the future of the Metronit on the shared trunk before any capacity work.'],
    s2_src='Source: executive decision summary of the comprehensive report.',
    s3_eyebrow='The question',
    s3_title='The main line to Nazareth is being built. The question is whether to continue it 18.7 km through Haifa to Tirat Carmel, and whether to run both as one line.',
    s3_alt='Map of the two lines: the extension from Tirat Carmel along the Haifa seafront to Hamifrats in blue, and the main route from Hamifrats to Nazareth in orange',
    s3_caption='Extension (blue, stations S01–S24) and main route (orange, M01–M20). Both meet at Hamifrats.',
    s3_facts=[('Extension', '24 stations, 18.7 km along the seafront and the lower city'), ('Tirat Carmel to Hamifrats', '41 minutes with priority at junctions; 66 minutes without'),
              ('Service assumed', 'A tram every 5 minutes, running through to Nazareth without a change'), ('Three choices on the table', 'Build the extension or not · one line or two · priority at junctions or not')],
    s3_src='Source: section 1 and Table 4.10 of the comprehensive report; map from Output/figures/lrt_alternatives_lines.png.',
    s4_eyebrow='How we answered it',
    s4_title='We took today’s travellers, grew them to 2050, and offered them the light rail as a new choice.',
    s4_steps=[('Today’s travel.', 'Who travels where in the morning peak, by car, bus, Metronit and train, from the household travel survey and smart-card ticketing, checked against traffic counts.'),
              ('Growth to 2040 and 2050.', 'The same travel pattern scaled by the official population and jobs forecasts. Corridor travel grows by 30 to 60 percent. Habits stay as they were in 2022.'),
              ('Today’s service, plus the light rail.', 'The May 2026 timetable and measured speeds for every bus, Metronit and car trip. The light rail is added as a new option; nothing else is cut or changed.'),
              ('Who switches.', 'Travellers pick the trip that feels shortest: riding, walking, waiting and changing vehicles all count. We count how many choose the light rail, and from which mode.')],
    s4_aside='The result is a corridor demand screening with a documented, reproducible chain of 45 steps. It is not a full regional transport model and not an economic appraisal.',
    s4_src='Source: section 2 of the comprehensive report.',
    s5_eyebrow='How many', s5_title='About 7,400 people would ride the line in the morning peak in 2050, and four in five of them use the extension.',
    s5_series=['Whole line (Tirat Carmel – Nazareth)', 'Of which use the extension'], s5_chart='LRT riders by scenario, morning 06:00–09:00',
    s5_caption='Morning LRT riders, 06:00–09:00, with priority at junctions. BU is business-as-usual growth; HS is the high-growth scenario.',
    s5_facts=[('Busiest hour, 2050', 'About 4,400 riders on the line'), ('Afternoon peak', 'About 85 percent of the morning'), ('Growth 2040 to 2050', 'About 18 percent, in step with the corridor'), ('High-growth scenario', 'Adds 15 to 25 percent in the same year')],
    s5_src='Source: Table 4.3 of the comprehensive report.',
    s6_eyebrow='Where', s6_title='The riders are in Haifa and Tirat Carmel: three markets of similar size make up three quarters of the demand.',
    s6_markets=['Tirat Carmel ↔ Haifa', 'Haifa internal (Matam – Hamifrats)', 'Krayot ↔ Haifa (by feeder)', 'Main route ↔ Haifa', 'Main route ↔ Krayot / Tirat Carmel', 'Within the main route', 'Krayot ↔ Tirat Carmel'],
    s6_chart='Where the LRT riders travel, 2050',
    s6_caption='Morning LRT riders by the areas at the two ends of their trip, 2050, both directions. Share of all 7,400 riders in brackets.',
    s6_facts=[('Largest single flow', 'Tirat Carmel ↔ Bat Galim, 820 riders a morning'), ('Crossing Hamifrats', '38 percent of riders travel between the two parts of the line'),
              ('The Krayot', 'Off the line; residents reach it by Metronit or bus feeder'), ('Main route beyond Kiryat Ata', 'A few hundred riders per direction')],
    s6_src='Source: Tables 4.5 and 4.7 of the comprehensive report.',
    s7_eyebrow='From where', s7_title='Most riders are today’s Metronit and bus passengers on a faster vehicle. The car gives up less than one trip in a hundred.',
    s7_sources=['From the Metronit', 'From buses', 'From cars'], s7_chart='Where the LRT riders come from, 2050',
    s7_keys=['Metronit: 33 % of its corridor passengers', 'Buses: 31 % of their corridor passengers', 'Cars: 0.9 % of corridor car trips'],
    s7_caption='Where the 7,400 morning LRT riders of 2050 come from.',
    s7_facts=[('Transit’s share of corridor travel', '19.3 % before the LRT, 20.6 % after'), ('What this means', 'The light rail reorganises transit more than it creates new travel'),
              ('What not to promise', 'Large relief on the roads. The car shift is a few hundred to a thousand trips, and it is the least certain number here')],
    s7_src='Source: Table 4.3 and section 4.4 of the comprehensive report.',
    s8_eyebrow='One line or two', s8_title='Running through to Nazareth does not add riders to the extension. What it buys is a saved change of vehicle for the 38 percent who cross Hamifrats.',
    s8_cats=['Riders using the extension', 'Riders on the whole line'], s8_series=['Extension ends at Hamifrats', 'One line through to Nazareth'], s8_chart='Through-running against terminating at Hamifrats, 2050',
    s8_caption='Morning riders in 2050, with priority at junctions. Terminating at Hamifrats was run; the main route alone was not.',
    s8_facts=[('Extension riders', '6,003 as one line, 5,939 if it ends at Hamifrats: a 1 percent difference'), ('The +25 % on the whole line', 'Is the main route’s own passengers, carried either way'),
              ('Who gains from one line', '2,849 riders a morning who would otherwise change trains at Hamifrats. The Metronit carries them through today')],
    s8_src='Source: Table 4.1 and section 4.1 of the comprehensive report.',
    s9_eyebrow='Priority at junctions', s9_title='Priority at the junctions is worth a quarter of the riders, more than ten years of growth.',
    s9_cats=['2040, with priority', '2050, with priority', '2050, no priority'], s9_series='Morning LRT riders', s9_chart='Priority at junctions against growth',
    s9_caption='Morning LRT riders on the whole line. "No priority" means the extension runs at street level and waits at junctions with the traffic.',
    s9_facts=[('Tirat Carmel to Hamifrats', '41 minutes with priority, 66 without'), ('Ten years of growth', 'Add 18 percent of riders'), ('Losing priority', 'Removes 23 percent, mostly on the extension itself'), ('In every scenario and period', 'The loss is 20 to 23 percent')],
    s9_src='Source: Tables 4.8 and 4.10 of the comprehensive report.',
    s10_eyebrow='How full', s10_title='In the busiest hour, about 1,000 to 1,100 passengers per direction pass the Hamifrats junction: a light-rail scale of demand, not a metro one.',
    s10_series='Passengers per hour, one direction', s10_chart='Busiest hour load at the Hamifrats junction',
    s10_caption='Busiest segment, busiest morning hour, one direction, with priority at junctions. These are potential movements with no capacity limit applied.',
    s10_facts=[('Busiest point', 'Entering Hamifrats towards Tirat Carmel in the morning'), ('On the extension itself', 'About 1,030 per hour in 2050, on the Carmel coast'), ('Afternoon', 'Lower and more balanced between the two directions')],
    s10_src='Source: Table 4.2a and section 4.5 of the comprehensive report.',
    s11_eyebrow='How sure', s11_title='A fair planning range is 5,500 to 10,500 morning riders. The central figure sits on the cautious side.',
    s11_low='Cautious case', s11_central='Central case', s11_high='Optimistic case', s11_unprio='No priority at junctions', s11_unprio2='a design choice, not an uncertainty', s11_axis='Morning LRT riders, 06:00–09:00, 2050', s11_chart='Planning range of morning LRT riders',
    s11_caption='The range comes from how strongly travellers respond to a faster trip, the widest single uncertainty tested.',
    s11_facts=[('Firm part', 'The switch from the Metronit and buses rests on observed travel and measured timetables'), ('Soft part', 'The switch from cars. Read it as an order of magnitude'),
               ('A cautious assumption', 'Roads and buses keep 2026 speeds in 2050. If buses slow with traffic, the LRT gains about 5 percent')],
    s11_src='Source: executive summary planning range; sections 3.4 and 4.9 of the comprehensive report.',
    s12_eyebrow='The open question', s12_title='The biggest open question is not in the model: will the Metronit and the light rail share the trunk?',
    s12_h1='What the model assumes', s12_l1=['Every Metronit and bus line keeps running next to the light rail, exactly as today.', 'About a third of Metronit passengers on the corridor switch; 7,800 stay because their trip is still quicker on the Metronit.', 'This is the cautious case for the light rail.'],
    s12_h2='What a network decision would do', s12_l2=['Cut the Metronit back on the overlap, and up to its 11,300 morning corridor trips could move to the light rail.', 'Reorganise the Metronit to feed the light-rail stations, and the light rail gains riders too.', 'Either choice moves the figures more than any uncertainty in this report. Settle it before using them for capacity.'],
    s12_src='Source: section 4.4 of the comprehensive report.',
    s13_eyebrow='Fitness for use', s13_title='Use these numbers to size the market and rank the options. Do not use them yet to buy trains or set frequencies.',
    s13_h_good='Good for', s13_good=['Sizing the extension’s market and locating it: which areas, which stations.', 'Ranking the options: one line or two, priority or not.', 'The order of magnitude of the draw from the Metronit, buses and cars.', 'The scale of the peak load, for the design hour.'],
    s13_h_bad='Not yet good for', s13_bad=['Fleet size, frequencies or capacity: the loads have no capacity limit and were not checked link by link.', 'An economic appraisal.', 'Any claim about road congestion in 2040 or 2050.', 'Numbers for a single station or a single neighbourhood.'],
    s13_src='Source: section 3.5 of the comprehensive report.',
    s14_eyebrow='The ask', s14_title='Five decisions we ask you to take.',
    s14_items=[('Plan on the 2050 reference case.', 'About 7,400 morning riders on the line, 6,000 of them on the extension, with 5,500 to 10,500 as the planning range.'),
               ('Protect priority at the junctions in the design.', 'Without it a quarter of the riders go, and the trip from Tirat Carmel to Hamifrats takes 66 minutes instead of 41.'),
               ('Treat through-running as a question of transfers, not of ridership.', 'One line spares 2,849 riders a morning a change of trains at Hamifrats; it does not add riders to the extension.'),
               ('Decide the future of the Metronit on the shared trunk', 'before any capacity or fleet work, because that decision moves the figures more than any uncertainty here.'),
               ('Commission four pieces of work before appraisal:', 'a split of trips by purpose, a proper afternoon forecast, the main route’s operating plan, and a survey of how willing car owners are to switch.')],
    s14_src='Source: executive decision summary and section 5 of the comprehensive report.',
    s15_eyebrow='In one breath', s15_title='A light-rail-sized market in Haifa and Tirat Carmel, carried mostly from today’s transit, that lives or dies on priority at the junctions.',
    s15_tiles=[('7,400', 'morning riders on the line in 2050; four in five on the extension'), ('3', 'markets of similar size: Tirat Carmel ↔ Haifa, Haifa internal, Krayot by feeder'),
               ('−23 %', 'without priority at junctions, more than ten years of growth adds'), ('+1 %', 'extension riders from running through to Nazareth; the gain is a saved transfer')],
    s15_aside='Next: settle the Metronit question, protect priority, and commission the four pieces of work before any appraisal or fleet decision.',
    s16_eyebrow='Appendix', s16_title='Where the numbers come from.',
    s16_h_data='Data behind the study',
    s16_data=['Household travel survey 2017/18: 16,401 people, 5,108 households.', 'Smart-card bus journeys, May 2022; boardings through 2025.', 'Population and jobs forecasts for 2040 and 2050, two scenarios (BU, HS).',
              'National timetable of 22 May 2026; measured bus and car speeds, May 2026.', 'Planned alignment and stations of the extension (22 Sep 2026) and the main route (5 Oct 2026).', 'Light-rail running times transferred from the Tel Aviv Red Line.'],
    s16_h_terms='Terms used here',
    s16_terms=[('BU / HS', ': business-as-usual and high-growth demographic scenarios.'), ('With priority', ': trams get the green at road junctions ("Prioritized" in the report). No priority: street running, queuing with traffic ("Unprioritized").'),
               ('Morning peak', ': trips leaving 06:00 to 09:00. The busiest hour is about 59 percent of that.'), ('Riders', ': boardings on the light rail, including trips that start or end on a feeder bus or Metronit.'),
               ('Corridor', ': 25 areas and 174 traffic zones from Tirat Carmel to Nazareth.')],
    s16_aside='Every figure traces to reports/Nofit_LRT_Extension_Comprehensive_Report.docx and the files under Output/ it names. This deck is built by tools/build_decision_deck.py.',
)
S['he'] = dict(
    lang='he', dir='rtl', title='תמצית החלטה: הארכת נופית',
    fonts='https://fonts.googleapis.com/css2?family=Heebo:wght@500;600;700&family=Assistant:wght@400;600&display=swap',
    display='"Heebo", "Arial Hebrew", Arial, sans-serif', body='"Assistant", "Arial Hebrew", system-ui, Arial, sans-serif',
    nav_title='הרכבת הקלה נופית · הארכה דרך חיפה לטירת כרמל', prev='הקודם ›', next='‹ הבא', prev_aria='השקופית הקודמת', next_aria='השקופית הבאה', slide_aria='שקופית',
    scen=['2022', '2040 רגיל', '2050 רגיל', '2040 גבוה', '2050 גבוה'],
    cover_eyebrow='תמצית למקבלי החלטות · הרכבת הקלה נופית · אוקטובר 2026',
    cover_title='האם להמשיך את הרכבת הקלה נופית דרך חיפה עד טירת כרמל?',
    cover_lede='מה אומרות הראיות על הביקוש לנסיעות, בשפה פשוטה. הוכן למקבלי החלטות מתוך הדוח המסכם של 5 באוקטובר 2026.',
    cover_facts=[('תרחיש הייחוס', 'שנת 2050, צמיחה רגילה, רכבת עם עדיפות בצמתים'), ('התקופה', 'שיא הבוקר, 06:00–09:00, אלא אם צוין אחרת'), ('ניווט', 'מקשי החצים, רווח, או הכפתורים למטה')],
    s2_eyebrow='התשובה בקצרה',
    s2_title='להארכה יש שוק אמיתי בסדר גודל של רכבת קלה. היא זקוקה לעדיפות בצמתים יותר משהיא זקוקה לקו רציף, והמספרים בשלים לקביעת גודל הקו, לא עדיין לרכישת קרונות.',
    s2_tiles=[('7,400', 'נוסעים בקו כולו בכל שיא בוקר ב-2050'), ('4 מתוך 5', 'מהם משתמשים בהארכה דרך חיפה'), ('−23 %', 'מהנוסעים אובדים אם הרכבת ממתינה בצמתים כמו מכונית')],
    s2_h_evidence='מה הראיות אומרות',
    s2_evidence=['הנוסעים נמצאים בחיפה ובטירת כרמל, בשלושה שווקים בגודל דומה.', 'רובם עוברים מהמטרונית ומהאוטובוסים. מעטים עוזבים את הרכב הפרטי.', 'קו רציף עד נצרת חוסך החלפת כלי רכב; הוא אינו מוסיף נוסעים להארכה.'],
    s2_h_ask='מה אנחנו מבקשים להחליט',
    s2_ask=['לתכנן על תרחיש הייחוס 2050, עם 5,500 עד 10,500 נוסעי בוקר כטווח.', 'לשמור בתכנון על עדיפות לרכבת בצמתים.', 'להכריע בעתיד המטרונית על הציר המשותף לפני כל עבודת קיבולת.'],
    s2_src='מקור: התמצית למקבלי ההחלטות בדוח המסכם.',
    s3_eyebrow='השאלה',
    s3_title='הקו הראשי עד נצרת נמצא בבנייה. השאלה היא אם להמשיך אותו 18.7 ק"מ דרך חיפה עד טירת כרמל, ואם להפעיל את שניהם כקו אחד.',
    s3_alt='מפת שני הקווים: ההארכה מטירת כרמל לאורך חוף חיפה עד המפרץ בכחול, והקו הראשי מהמפרץ לנצרת בכתום',
    s3_caption='ההארכה (כחול, תחנות S01–S24) והקו הראשי (כתום, M01–M20). שניהם נפגשים במפרץ. כיתובי המפה באנגלית.',
    s3_facts=[('ההארכה', '24 תחנות, 18.7 ק"מ לאורך חוף הים והעיר התחתית'), ('מטירת כרמל למפרץ', '41 דקות עם עדיפות בצמתים; 66 דקות בלעדיה'),
              ('השירות שהונח', 'רכבת כל 5 דקות, שנוסעת ברצף עד נצרת ללא החלפה'), ('שלוש הכרעות על השולחן', 'לבנות את ההארכה או לא · קו אחד או שניים · עדיפות בצמתים או לא')],
    s3_src='מקור: פרק 1 וטבלה 4.10 בדוח המסכם; המפה מתוך Output/figures/lrt_alternatives_lines.png.',
    s4_eyebrow='איך ענינו',
    s4_title='לקחנו את הנוסעים של היום, הגדלנו אותם ל-2050, והצענו להם את הרכבת הקלה כאפשרות חדשה.',
    s4_steps=[('הנסיעות של היום.', 'מי נוסע לאן בשיא הבוקר, ברכב, באוטובוס, במטרונית וברכבת, מסקר הנסיעות של משקי הבית ומכרטוס הרב-קו, בבדיקה מול ספירות תנועה.'),
              ('צמיחה ל-2040 ול-2050.', 'אותה תבנית נסיעות, מוגדלת לפי תחזיות האוכלוסייה והתעסוקה הרשמיות. הנסיעות במסדרון גדלות ב-30 עד 60 אחוז. ההרגלים נשארים כמו ב-2022.'),
              ('השירות של היום, ועליו הרכבת הקלה.', 'לוח הזמנים של מאי 2026 והמהירויות שנמדדו לכל נסיעת אוטובוס, מטרונית ורכב. הרכבת הקלה מתווספת כאפשרות חדשה; שום דבר אחר לא מבוטל ולא משתנה.'),
              ('מי עובר.', 'הנוסעים בוחרים בנסיעה שמרגישה הקצרה ביותר: הנסיעה עצמה, ההליכה, ההמתנה והחלפות כלי הרכב כולן נספרות. אנחנו סופרים כמה בוחרים ברכבת הקלה, ומאיזה אמצעי.')],
    s4_aside='התוצאה היא סינון ביקוש למסדרון, בשרשרת מתועדת וניתנת לשחזור של 45 שלבים. זה אינו מודל תחבורה אזורי מלא ואינו הערכה כלכלית.',
    s4_src='מקור: פרק 2 בדוח המסכם.',
    s5_eyebrow='כמה', s5_title='כ-7,400 איש ייסעו בקו בשיא הבוקר ב-2050, וארבעה מכל חמישה מהם משתמשים בהארכה.',
    s5_series=['הקו כולו (טירת כרמל – נצרת)', 'מתוכם משתמשים בהארכה'], s5_chart='נוסעי הרכבת הקלה לפי תרחיש, בוקר 06:00–09:00',
    s5_caption='נוסעי בוקר ברכבת הקלה, 06:00–09:00, עם עדיפות בצמתים. "רגיל" הוא תרחיש הצמיחה הרגיל; "גבוה" הוא תרחיש הצמיחה הגבוה.',
    s5_facts=[('שעת השיא, 2050', 'כ-4,400 נוסעים בקו'), ('שיא אחר הצהריים', 'כ-85 אחוז מהבוקר'), ('צמיחה מ-2040 ל-2050', 'כ-18 אחוז, בקצב המסדרון'), ('תרחיש הצמיחה הגבוה', 'מוסיף 15 עד 25 אחוז באותה שנה')],
    s5_src='מקור: טבלה 4.3 בדוח המסכם.',
    s6_eyebrow='איפה', s6_title='הנוסעים נמצאים בחיפה ובטירת כרמל: שלושה שווקים בגודל דומה מהווים שלושה רבעים מהביקוש.',
    s6_markets=['טירת כרמל ↔ חיפה', 'בתוך חיפה (מת"ם – המפרץ)', 'הקריות ↔ חיפה (בהזנה)', 'הקו הראשי ↔ חיפה', 'הקו הראשי ↔ הקריות / טירת כרמל', 'בתוך הקו הראשי', 'הקריות ↔ טירת כרמל'],
    s6_chart='לאן נוסעים נוסעי הרכבת הקלה, 2050',
    s6_caption='נוסעי בוקר ברכבת הקלה לפי האזורים בשני קצות הנסיעה, 2050, שני הכיוונים. בסוגריים החלק מכלל 7,400 הנוסעים.',
    s6_facts=[('הזרם הבודד הגדול ביותר', 'טירת כרמל ↔ בת גלים, 820 נוסעים בבוקר'), ('חציית המפרץ', '38 אחוז מהנוסעים נוסעים בין שני חלקי הקו'),
              ('הקריות', 'מחוץ לקו; התושבים מגיעים אליו במטרונית או באוטובוס מזין'), ('הקו הראשי מעבר לקריית אתא', 'כמה מאות נוסעים לכיוון')],
    s6_src='מקור: טבלאות 4.5 ו-4.7 בדוח המסכם.',
    s7_eyebrow='מאיפה', s7_title='רוב הנוסעים הם נוסעי המטרונית והאוטובוסים של היום בכלי מהיר יותר. הרכב הפרטי מוותר על פחות מנסיעה אחת ממאה.',
    s7_sources=['מהמטרונית', 'מאוטובוסים', 'מרכב פרטי'], s7_chart='מאיפה מגיעים נוסעי הרכבת הקלה, 2050',
    s7_keys=['מטרונית: 33 % מנוסעיה במסדרון', 'אוטובוסים: 31 % מנוסעיהם במסדרון', 'רכב פרטי: 0.9 % מנסיעות הרכב במסדרון'],
    s7_caption='מאיפה מגיעים 7,400 נוסעי הבוקר של הרכבת הקלה ב-2050.',
    s7_facts=[('חלק התחבורה הציבורית בנסיעות במסדרון', '19.3 % לפני הרכבת הקלה, 20.6 % אחריה'), ('מה זה אומר', 'הרכבת הקלה מארגנת מחדש את התחבורה הציבורית יותר משהיא יוצרת נסיעות חדשות'),
              ('מה לא להבטיח', 'הקלה גדולה בכבישים. המעבר מהרכב הוא כמה מאות עד כאלף נסיעות, והוא המספר הכי פחות ודאי כאן')],
    s7_src='מקור: טבלה 4.3 ופרק 4.4 בדוח המסכם.',
    s8_eyebrow='קו אחד או שניים', s8_title='קו רציף עד נצרת אינו מוסיף נוסעים להארכה. מה שהוא קונה הוא החלפת כלי רכב שנחסכת ל-38 האחוזים שחוצים את המפרץ.',
    s8_cats=['נוסעים שמשתמשים בהארכה', 'נוסעים בקו כולו'], s8_series=['ההארכה מסתיימת במפרץ', 'קו אחד רציף עד נצרת'], s8_chart='קו רציף לעומת סיום במפרץ, 2050',
    s8_caption='נוסעי בוקר ב-2050, עם עדיפות בצמתים. סיום במפרץ נבדק; הקו הראשי לבדו לא.',
    s8_facts=[('נוסעי ההארכה', '6,003 כקו אחד, 5,939 אם היא מסתיימת במפרץ: הבדל של אחוז אחד'), ('ה-25 % הנוספים בקו כולו', 'הם נוסעי הקו הראשי עצמו, שנוסעים בכל מקרה'),
              ('מי מרוויח מקו אחד', '2,849 נוסעים בבוקר שאחרת היו מחליפים רכבת במפרץ. המטרונית מסיעה אותם היום ברצף')],
    s8_src='מקור: טבלה 4.1 ופרק 4.1 בדוח המסכם.',
    s9_eyebrow='עדיפות בצמתים', s9_title='עדיפות בצמתים שווה רבע מהנוסעים, יותר מעשר שנות צמיחה.',
    s9_cats=['2040, עם עדיפות', '2050, עם עדיפות', '2050, בלי עדיפות'], s9_series='נוסעי בוקר ברכבת הקלה', s9_chart='עדיפות בצמתים לעומת צמיחה',
    s9_caption='נוסעי בוקר ברכבת הקלה בקו כולו. "בלי עדיפות" פירושו שההארכה נוסעת ברמת הרחוב וממתינה בצמתים עם התנועה.',
    s9_facts=[('מטירת כרמל למפרץ', '41 דקות עם עדיפות, 66 בלעדיה'), ('עשר שנות צמיחה', 'מוסיפות 18 אחוז נוסעים'), ('אובדן העדיפות', 'מוריד 23 אחוז, רובם על ההארכה עצמה'), ('בכל תרחיש ותקופה', 'ההפסד הוא 20 עד 23 אחוז')],
    s9_src='מקור: טבלאות 4.8 ו-4.10 בדוח המסכם.',
    s10_eyebrow='כמה עמוס', s10_title='בשעה העמוסה ביותר עוברים בצומת המפרץ כ-1,000 עד 1,100 נוסעים לכיוון: ביקוש בסדר גודל של רכבת קלה, לא של מטרו.',
    s10_series='נוסעים לשעה, כיוון אחד', s10_chart='עומס השעה העמוסה בצומת המפרץ',
    s10_caption='הקטע העמוס ביותר, שעת שיא הבוקר, כיוון אחד, עם עדיפות בצמתים. אלה תנועות פוטנציאליות ללא מגבלת קיבולת.',
    s10_facts=[('הנקודה העמוסה ביותר', 'הכניסה למפרץ לכיוון טירת כרמל בבוקר'), ('על ההארכה עצמה', 'כ-1,030 לשעה ב-2050, על חוף הכרמל'), ('אחר הצהריים', 'נמוך יותר ומאוזן יותר בין שני הכיוונים')],
    s10_src='מקור: טבלה 4.2a ופרק 4.5 בדוח המסכם.',
    s11_eyebrow='כמה בטוח', s11_title='טווח תכנון הוגן הוא 5,500 עד 10,500 נוסעי בוקר. המספר המרכזי נמצא בצד הזהיר.',
    s11_low='המקרה הזהיר', s11_central='המקרה המרכזי', s11_high='המקרה האופטימי', s11_unprio='בלי עדיפות בצמתים', s11_unprio2='החלטת תכנון, לא אי-ודאות', s11_axis='נוסעי בוקר ברכבת הקלה, 06:00–09:00, 2050', s11_chart='טווח התכנון של נוסעי הבוקר',
    s11_caption='הטווח נובע מעד כמה הנוסעים מגיבים לנסיעה מהירה יותר, אי-הוודאות הבודדת הרחבה ביותר שנבדקה.',
    s11_facts=[('החלק המוצק', 'המעבר מהמטרונית ומהאוטובוסים נשען על נסיעות שנצפו ועל לוחות זמנים שנמדדו'), ('החלק הרך', 'המעבר מהרכב הפרטי. יש לקרוא אותו כסדר גודל'),
               ('הנחה זהירה', 'הכבישים והאוטובוסים שומרים על מהירויות 2026 גם ב-2050. אם האוטובוסים יואטו בפקקים, הרכבת הקלה מרוויחה כ-5 אחוז')],
    s11_src='מקור: טווח התכנון בתמצית; פרקים 3.4 ו-4.9 בדוח המסכם.',
    s12_eyebrow='השאלה הפתוחה', s12_title='השאלה הפתוחה הגדולה ביותר אינה במודל: האם המטרונית והרכבת הקלה יחלקו את הציר?',
    s12_h1='מה המודל מניח', s12_l1=['כל קו מטרונית ואוטובוס ממשיך לנסוע לצד הרכבת הקלה, בדיוק כמו היום.', 'כשליש מנוסעי המטרונית במסדרון עוברים; 7,800 נשארים כי נסיעתם עדיין מהירה יותר במטרונית.', 'זהו המקרה הזהיר עבור הרכבת הקלה.'],
    s12_h2='מה תעשה החלטה על הרשת', s12_l2=['צמצום המטרונית בקטע החופף, ועד 11,300 נסיעות הבוקר שלה במסדרון עשויות לעבור לרכבת הקלה.', 'ארגון מחדש של המטרונית כמזינה לתחנות הרכבת הקלה, והרכבת הקלה מרוויחה נוסעים גם כך.', 'כל אחת מההכרעות מזיזה את המספרים יותר מכל אי-ודאות בדוח הזה. יש להכריע בה לפני שמשתמשים בהם לקיבולת.'],
    s12_src='מקור: פרק 4.4 בדוח המסכם.',
    s13_eyebrow='למה המספרים מתאימים', s13_title='להשתמש במספרים האלה כדי לאמוד את השוק ולדרג את החלופות. לא להשתמש בהם עדיין כדי לרכוש קרונות או לקבוע תדירויות.',
    s13_h_good='מתאים ל', s13_good=['אומדן שוק ההארכה ומיקומו: אילו אזורים, אילו תחנות.', 'דירוג החלופות: קו אחד או שניים, עדיפות או לא.', 'סדר הגודל של המעבר מהמטרונית, מהאוטובוסים ומהרכב.', 'סדר הגודל של עומס השיא, לשעת התכן.'],
    s13_h_bad='עדיין לא מתאים ל', s13_bad=['גודל הצי, תדירויות או קיבולת: לעומסים אין מגבלת קיבולת והם לא נבדקו קטע-קטע.', 'הערכה כלכלית.', 'כל טענה על עומסי תנועה בכבישים ב-2040 או ב-2050.', 'מספרים לתחנה בודדת או לשכונה בודדת.'],
    s13_src='מקור: פרק 3.5 בדוח המסכם.',
    s14_eyebrow='הבקשה', s14_title='חמש הכרעות שאנחנו מבקשים לקבל.',
    s14_items=[('לתכנן על תרחיש הייחוס 2050.', 'כ-7,400 נוסעי בוקר בקו, 6,000 מהם על ההארכה, עם 5,500 עד 10,500 כטווח התכנון.'),
               ('לשמור בתכנון על עדיפות בצמתים.', 'בלעדיה רבע מהנוסעים הולכים לאיבוד, והנסיעה מטירת כרמל למפרץ נמשכת 66 דקות במקום 41.'),
               ('להתייחס לקו הרציף כשאלה של מעברים, לא של מספר נוסעים.', 'קו אחד חוסך ל-2,849 נוסעים בבוקר החלפת רכבת במפרץ; הוא אינו מוסיף נוסעים להארכה.'),
               ('להכריע בעתיד המטרונית על הציר המשותף', 'לפני כל עבודת קיבולת או צי, כי ההכרעה הזאת מזיזה את המספרים יותר מכל אי-ודאות כאן.'),
               ('להזמין ארבע עבודות לפני הערכה כלכלית:', 'פיצול הנסיעות לפי מטרה, תחזית אחר-צהריים מסודרת, תוכנית ההפעלה של הקו הראשי, וסקר על נכונות בעלי הרכב לעבור.')],
    s14_src='מקור: התמצית למקבלי ההחלטות ופרק 5 בדוח המסכם.',
    s15_eyebrow='בנשימה אחת', s15_title='שוק בסדר גודל של רכבת קלה בחיפה ובטירת כרמל, שרובו מגיע מהתחבורה הציבורית של היום, ושחי או מת על עדיפות בצמתים.',
    s15_tiles=[('7,400', 'נוסעי בוקר בקו ב-2050; ארבעה מכל חמישה על ההארכה'), ('3', 'שווקים בגודל דומה: טירת כרמל ↔ חיפה, בתוך חיפה, הקריות בהזנה'),
               ('−23 %', 'בלי עדיפות בצמתים, יותר ממה שעשר שנות צמיחה מוסיפות'), ('+1 %', 'נוסעי הארכה מקו רציף עד נצרת; הרווח הוא מעבר שנחסך')],
    s15_aside='הצעד הבא: להכריע בשאלת המטרונית, לשמור על העדיפות, ולהזמין את ארבע העבודות לפני כל הערכה כלכלית או החלטה על צי.',
    s16_eyebrow='נספח', s16_title='מאיפה המספרים.',
    s16_h_data='הנתונים מאחורי המחקר',
    s16_data=['סקר הנסיעות של משקי הבית 2017/18: 16,401 אנשים, 5,108 משקי בית.', 'נסיעות אוטובוס מכרטוס הרב-קו, מאי 2022; עליות עד 2025.', 'תחזיות אוכלוסייה ותעסוקה ל-2040 ול-2050, שני תרחישים (רגיל, גבוה).',
              'לוח הזמנים הארצי של 22 במאי 2026; מהירויות אוטובוס ורכב שנמדדו, מאי 2026.', 'התוואי והתחנות המתוכננים של ההארכה (22 בספטמבר 2026) ושל הקו הראשי (5 באוקטובר 2026).', 'זמני הנסיעה של הרכבת הקלה הועברו מהקו האדום בתל אביב.'],
    s16_h_terms='מונחים',
    s16_terms=[('רגיל / גבוה', ': התרחישים הדמוגרפיים הרגיל והגבוה (BU / HS בדוח).'), ('עם עדיפות', ': הרכבת מקבלת ירוק בצמתים ("Prioritized" בדוח). בלי עדיפות: נסיעה ברמת הרחוב, המתנה עם התנועה ("Unprioritized").'),
               ('שיא הבוקר', ': נסיעות שיוצאות בין 06:00 ל-09:00. השעה העמוסה היא כ-59 אחוז מהן.'), ('נוסעים', ': עליות לרכבת הקלה, כולל נסיעות שמתחילות או מסתיימות באוטובוס מזין או במטרונית.'),
               ('המסדרון', ': 25 אזורים ו-174 אזורי תנועה מטירת כרמל עד נצרת.')],
    s16_aside='כל מספר ניתן לאיתור בדוח reports/Nofit_LRT_Extension_Comprehensive_Report.docx ובקבצים תחת Output/ שהוא מציין. המצגת נבנית על ידי tools/build_decision_deck.py.',
)

# ---------------- SVG chart helpers (marks: bars <= 24 px, 4 px rounded data-end, square at the baseline; hairline grid) ----------------
def fmt(n): return f'{n:,.0f}'
def col_path(x, y, w, h, r=4):
    """Column standing on the baseline y+h, rounded at the top only."""
    if h <= r: return f'M{x},{y + h} v{-h} h{w} v{h} z'
    return f'M{x},{y + h} v{-(h - r)} a{r},{r} 0 0 1 {r},{-r} h{w - 2 * r} a{r},{r} 0 0 1 {r},{r} v{h - r} z'
def bar_path(x, y, w, h, r=4, rtl=False):
    """Horizontal bar growing from x to the right (or, rtl, from x to the left), rounded at the data end only."""
    if w <= r: return f'M{x},{y} h{-w if rtl else w} v{h} h{w if rtl else -w} z'
    if rtl: return f'M{x},{y} h{-(w - r)} a{r},{r} 0 0 0 {-r},{r} v{h - 2 * r} a{r},{r} 0 0 0 {r},{r} h{w - r} z'
    return f'M{x},{y} h{w - r} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r} a{r},{r} 0 0 1 {-r},{r} h{-(w - r)} z'
def nice_ticks(vmax, n=4):
    import math
    raw = vmax / n; mag = 10 ** math.floor(math.log10(raw)); step = min(s for s in (1, 2, 2.5, 5, 10) if s * mag >= raw) * mag
    ticks = []; v = 0
    while v <= vmax + 1e-9: ticks.append(v); v += step
    if ticks[-1] < vmax: ticks.append(ticks[-1] + step)
    return ticks

def grouped_columns(cats, series, title, width=640, height=340, legend=True, cap=None):
    """series: list of (name, class, values). One y scale, columns in groups, 2 px surface gap between neighbours. Years run left to right in both languages."""
    L, R, T, B = 56, 12, 16, 56
    pw, ph = width - L - R, height - T - B
    vmax = max(max(v) for _, _, v in series) if cap is None else cap
    ticks = nice_ticks(vmax); ymax = ticks[-1]
    def y(v): return T + ph - ph * v / ymax
    bw = min(24, (pw / len(cats) - 16) / len(series) - 2)
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    for t in ticks:
        out.append(f'<line class="grid" x1="{L}" x2="{L + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>')
        out.append(f'<text class="tick" x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{fmt(t)}</text>')
    for i, c in enumerate(cats):
        gx = L + pw * (i + 0.5) / len(cats); gw = len(series) * (bw + 2) - 2; x0 = gx - gw / 2
        for j, (name, cls, vals) in enumerate(series):
            v = vals[i]; x = x0 + j * (bw + 2); top = y(v)
            out.append(f'<path class="mark {cls}" d="{col_path(x, top, bw, T + ph - top)}"><title>{c} · {name}: {fmt(v)}</title></path>')
            # value on the cap; in a pair the labels split around the gap so they never collide
            lx, anchor = (x + bw / 2, 'middle') if len(series) == 1 else ((x + bw, 'end') if j == 0 else (x, 'start'))
            out.append(f'<text class="vlabel" x="{lx:.1f}" y="{top - 6:.1f}" text-anchor="{anchor}">{fmt(v)}</text>')
        out.append(f'<text class="cat" x="{gx:.1f}" y="{T + ph + 20}" text-anchor="middle">{c}</text>')
    out.append(f'<line class="axis" x1="{L}" x2="{L + pw}" y1="{T + ph}" y2="{T + ph}"/>')
    if legend and len(series) > 1:
        # the legend is laid out as HTML below the plot (handles both reading directions); nothing drawn here
        pass
    out.append('</svg>'); return '\n'.join(out)

def html_legend(series):
    return '<ul class="keylist">' + ''.join(f'<li><span class="sw {cls}"></span>{name}</li>' for name, cls, _ in series) + '</ul>'

def hbars(labels, values, title, rtl=False, width=640, row_h=34, label_w=250, classes=None, total=None):
    """Bars grow from the label column: rightwards (labels on the left) or, rtl, leftwards (labels on the right)."""
    T = 8; height = T + row_h * len(labels) + 8; val_w = 110; pw = width - label_w - val_w
    vmax = max(values); bw = 22
    x0 = width - label_w if rtl else label_w          # the baseline
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    for i, (lab, v) in enumerate(zip(labels, values)):
        yy = T + i * row_h + (row_h - bw) / 2; w = pw * v / vmax; c = classes[i] if classes else 'c1'
        out.append(f'<text class="cat" x="{x0 + (12 if rtl else -12)}" y="{yy + bw / 2 + 4:.1f}" text-anchor="{"start" if rtl else "end"}">{lab}</text>')
        out.append(f'<path class="mark {c}" d="{bar_path(x0, yy, w, bw, rtl=rtl)}"><title>{lab}: {fmt(v)}</title></path>')
        val = fmt(v) + (f' <tspan class="share">({v / total:.0%})</tspan>' if total else '')
        out.append(f'<text class="vlabel" x="{x0 - w - 8 if rtl else x0 + w + 8:.1f}" y="{yy + bw / 2 + 4:.1f}" text-anchor="{"end" if rtl else "start"}">{val}</text>')
    out.append(f'<line class="axis" x1="{x0}" x2="{x0}" y1="{T}" y2="{T + row_h * len(labels)}"/>')
    out.append('</svg>'); return '\n'.join(out)

def range_chart(t, width=640, height=196):
    """The planning range as one horizontal scale (numbers run left to right in both languages): low, central, high, plus the design choice as a hollow marker."""
    L, R = 40, 140; pw = width - L - R; vmin, vmax = 0, 12000; yb = 84   # R leaves room for the label right of the optimistic dot
    def x(v): return L + pw * (v - vmin) / (vmax - vmin)
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{t["s11_chart"]}">']
    for tk in range(0, 12001, 2000):
        out.append(f'<line class="grid" x1="{x(tk):.1f}" x2="{x(tk):.1f}" y1="{yb - 30}" y2="{yb + 64}"/>')
        out.append(f'<text class="tick" x="{x(tk):.1f}" y="{yb + 80}" text-anchor="middle">{fmt(tk)}</text>')
    lo, ce, hi, un = RANGE['low'], RANGE['central'], RANGE['high'], RANGE['unprioritized']
    out.append(f'<rect class="mark c1 wash" x="{x(lo):.1f}" y="{yb - 10}" width="{x(hi) - x(lo):.1f}" height="20" rx="4"/>')
    out.append(f'<line class="mark-line c1" x1="{x(lo):.1f}" x2="{x(hi):.1f}" y1="{yb}" y2="{yb}"/>')
    for v, lab, anchor in ((lo, t['s11_low'], 'end'), (hi, t['s11_high'], 'start')):
        out.append(f'<circle class="dot c1" cx="{x(v):.1f}" cy="{yb}" r="6"/>')
        out.append(f'<text class="vlabel" x="{x(v) + (12 if anchor == "start" else -12):.1f}" y="{yb + 4}" text-anchor="{anchor}">{lab}: {fmt(v)}</text>')
    out.append(f'<circle class="dot c1" cx="{x(ce):.1f}" cy="{yb}" r="9"/>')
    out.append(f'<text class="vlabel strong" x="{x(ce):.1f}" y="{yb - 22}" text-anchor="middle">{t["s11_central"]}: {fmt(ce)}</text>')
    out.append(f'<circle class="dot hollow" cx="{x(un):.1f}" cy="{yb + 40}" r="6"/>')
    out.append(f'<text class="note" x="{x(un) + 12:.1f}" y="{yb + 37}">{t["s11_unprio"]}: {fmt(un)}</text>')
    out.append(f'<text class="note" x="{x(un) + 12:.1f}" y="{yb + 52}">{t["s11_unprio2"]}</text>')
    out.append(f'<text class="tick" x="{L}" y="{yb + 100}">{t["s11_axis"]}</text>')
    out.append('</svg>'); return '\n'.join(out)

def map_data_uri():
    from PIL import Image
    im = Image.open(MAP_PNG).convert('RGB').crop((120, 120, 1620, 960)); im.thumbnail((1200, 800))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=82, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

# ---------------- the slides ----------------
def facts(items): return '<div class="facts">' + ''.join(f'<div><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in items) + '</div>'
def ul(items, cls=''): return f'<ul class="{cls}">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def chart_slide(chart, caption, fact_items, legend=''):
    return f'<div class="cols chart-cols"><div class="chartbox">{chart}{legend}<p class="caption">{caption}</p></div>{facts(fact_items)}</div>'

def build(lang):
    t = S[lang]; rtl = t['dir'] == 'rtl'; MAP = map_data_uri()
    ch_demand = grouped_columns(t['scen'], [(t['s5_series'][0], 'c2', LRT_TOTAL), (t['s5_series'][1], 'c1', LRT_EXT)], t['s5_chart'], cap=10000)
    ch_markets = hbars(t['s6_markets'], MARKETS, t['s6_chart'], rtl=rtl, total=sum(MARKETS))
    ch_sources = hbars(t['s7_sources'], SOURCES, t['s7_chart'], rtl=rtl, classes=['o1', 'o2', 'o3'])
    ch_through = grouped_columns(t['s8_cats'], [(t['s8_series'][0], 'c3', list(THROUGH['ext_only'])), (t['s8_series'][1], 'c1', list(THROUGH['through']))], t['s8_chart'], cap=8500)
    ch_regime = grouped_columns(t['s9_cats'], [(t['s9_series'], 'c1', REGIME)], t['s9_chart'], legend=False, cap=8500)
    ch_peak = grouped_columns(t['scen'], [(t['s10_series'], 'c1', PEAK_LOAD)], t['s10_chart'], legend=False, cap=1600)
    ch_range = range_chart(t)
    n = [0]
    def slide(kind, eyebrow, title, body, source=''):
        n[0] += 1; src = f'<p class="source">{source}</p>' if source else ''
        return f'<section class="slide {kind}" id="s{n[0]}" aria-label="{t["slide_aria"]} {n[0]}">\n  <div class="inner">\n    <p class="eyebrow">{eyebrow}</p>\n    <h2>{title}</h2>\n    {body}\n    {src}\n  </div>\n</section>'
    slides = []
    n[0] += 1
    slides.append(f'''<section class="slide cover" id="s1" aria-label="{t['slide_aria']} 1">
  <div class="inner">
    <p class="eyebrow">{t['cover_eyebrow']}</p>
    <h1>{t['cover_title']}</h1>
    <p class="lede">{t['cover_lede']}</p>
    <div class="cover-facts">{''.join(f'<div><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in t['cover_facts'])}</div>
  </div>
</section>''')
    slides.append(slide('answer', t['s2_eyebrow'], t['s2_title'],
        '<div class="tiles">' + ''.join(f'<div class="tile"><span class="big">{b}</span><span class="lab">{l}</span></div>' for b, l in t['s2_tiles']) + '</div>'
        + f'<div class="cols"><div><h3>{t["s2_h_evidence"]}</h3>{ul(t["s2_evidence"])}</div><div><h3>{t["s2_h_ask"]}</h3>{ul(t["s2_ask"])}</div></div>', t['s2_src']))
    slides.append(slide('map', t['s3_eyebrow'], t['s3_title'],
        f'<div class="cols map-cols"><figure class="mapfig"><img src="{MAP}" alt="{t["s3_alt"]}"><figcaption>{t["s3_caption"]}</figcaption></figure>{facts(t["s3_facts"])}</div>', t['s3_src']))
    slides.append(slide('method', t['s4_eyebrow'], t['s4_title'],
        '<ol class="steps">' + ''.join(f'<li><span class="n">{i + 1}</span><div><strong>{h}</strong> {b}</div></li>' for i, (h, b) in enumerate(t['s4_steps'])) + '</ol>'
        + f'<p class="aside">{t["s4_aside"]}</p>', t['s4_src']))
    slides.append(slide('chart', t['s5_eyebrow'], t['s5_title'], chart_slide(ch_demand, t['s5_caption'], t['s5_facts'], html_legend([(t['s5_series'][0], 'c2', 0), (t['s5_series'][1], 'c1', 0)])), t['s5_src']))
    slides.append(slide('chart', t['s6_eyebrow'], t['s6_title'], chart_slide(ch_markets, t['s6_caption'], t['s6_facts']), t['s6_src']))
    slides.append(slide('chart', t['s7_eyebrow'], t['s7_title'], chart_slide(ch_sources, t['s7_caption'], t['s7_facts'], html_legend([(k, c, 0) for k, c in zip(t['s7_keys'], ['o1', 'o2', 'o3'])])), t['s7_src']))
    slides.append(slide('chart', t['s8_eyebrow'], t['s8_title'], chart_slide(ch_through, t['s8_caption'], t['s8_facts'], html_legend([(t['s8_series'][0], 'c3', 0), (t['s8_series'][1], 'c1', 0)])), t['s8_src']))
    slides.append(slide('chart', t['s9_eyebrow'], t['s9_title'], chart_slide(ch_regime, t['s9_caption'], t['s9_facts']), t['s9_src']))
    slides.append(slide('chart', t['s10_eyebrow'], t['s10_title'], chart_slide(ch_peak, t['s10_caption'], t['s10_facts']), t['s10_src']))
    slides.append(slide('chart', t['s11_eyebrow'], t['s11_title'], chart_slide(ch_range, t['s11_caption'], t['s11_facts']), t['s11_src']))
    slides.append(slide('text', t['s12_eyebrow'], t['s12_title'],
        f'<div class="cols"><div><h3>{t["s12_h1"]}</h3>{ul(t["s12_l1"])}</div><div><h3>{t["s12_h2"]}</h3>{ul(t["s12_l2"])}</div></div>', t['s12_src']))
    slides.append(slide('text', t['s13_eyebrow'], t['s13_title'],
        f'<div class="cols fit"><div class="good"><h3>{t["s13_h_good"]}</h3>{ul(t["s13_good"])}</div><div class="bad"><h3>{t["s13_h_bad"]}</h3>{ul(t["s13_bad"])}</div></div>', t['s13_src']))
    slides.append(slide('cta', t['s14_eyebrow'], t['s14_title'],
        '<ol class="decisions">' + ''.join(f'<li><span class="n">{i + 1}</span><div><strong>{h}</strong> {b}</div></li>' for i, (h, b) in enumerate(t['s14_items'])) + '</ol>', t['s14_src']))
    slides.append(slide('recap', t['s15_eyebrow'], t['s15_title'],
        '<div class="recap-grid">' + ''.join(f'<div><span class="big">{b}</span><span class="lab">{l}</span></div>' for b, l in t['s15_tiles']) + '</div>' + f'<p class="aside">{t["s15_aside"]}</p>'))
    slides.append(slide('appendix', t['s16_eyebrow'], t['s16_title'],
        f'<div class="cols"><div><h3>{t["s16_h_data"]}</h3>{ul(t["s16_data"], "tight")}</div><div><h3>{t["s16_h_terms"]}</h3>'
        + '<ul class="tight">' + ''.join(f'<li><strong>{k}</strong>{v}</li>' for k, v in t['s16_terms']) + '</ul></div></div>' + f'<p class="aside">{t["s16_aside"]}</p>'))

    head = f'''<title>{t['title']}</title>
<link rel="stylesheet" href="{t['fonts']}">
<style>
/* Layout: one slide per screen, scroll-snapped vertically; a fixed bottom bar with the counter. Signage-like type, cool neutrals, LRT blue as the accent.
   Logical properties throughout so the same sheet serves the left-to-right and the right-to-left deck. */
:root {{
  --bg: #eef1f5; --surface: #ffffff; --ink: #14202e; --ink-2: #4b5665; --muted: #7d8794; --hair: #d9dee6; --grid: #e6eaf0;
  --accent: #2a78d6; --accent-ink: #1c5cab; --orange: #eb6834; --aqua: #1baf7a; --wash: rgba(42,120,214,0.12);
  --o1: #184f95; --o2: #3987e5; --o3: #86b6ef; --good: #006300; --bad: #b3261e;
  --display: {t['display']}; --body: {t['body']};
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0f1419; --surface: #1a2028; --ink: #f2f4f7; --ink-2: #b4bcc7; --muted: #8b95a1; --hair: #2c343e; --grid: #242c36;
  --accent: #3987e5; --accent-ink: #86b6ef; --orange: #d95926; --aqua: #199e70; --wash: rgba(57,135,229,0.18);
  --o1: #86b6ef; --o2: #3987e5; --o3: #1c5cab; --good: #4fc24f; --bad: #f28b82; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0f1419; --surface: #1a2028; --ink: #f2f4f7; --ink-2: #b4bcc7; --muted: #8b95a1; --hair: #2c343e; --grid: #242c36;
  --accent: #3987e5; --accent-ink: #86b6ef; --orange: #d95926; --aqua: #199e70; --wash: rgba(57,135,229,0.18);
  --o1: #86b6ef; --o2: #3987e5; --o3: #1c5cab; --good: #4fc24f; --bad: #f28b82; color-scheme: dark; }}
html, body {{ height: 100%; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 17px; line-height: 1.5; }}
.page {{ height: 100%; }}
.deck {{ height: 100%; overflow-y: auto; scroll-snap-type: y mandatory; scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ .deck {{ scroll-behavior: auto; }} }}
.slide {{ min-height: 100%; box-sizing: border-box; scroll-snap-align: start; display: flex; align-items: center; padding: 24px 16px 72px; border-bottom: 1px solid var(--hair); }}
.inner {{ width: 100%; max-width: 1080px; margin: 0 auto; display: flex; flex-direction: column; gap: 18px; min-width: 0; overflow-wrap: anywhere; }}
.eyebrow {{ margin: 0; font-family: var(--display); font-weight: 600; font-size: 0.8rem; letter-spacing: {'0.02em' if rtl else '0.08em'}; text-transform: uppercase; color: var(--accent-ink); }}
h1, h2, h3 {{ font-family: var(--display); margin: 0; text-wrap: balance; line-height: 1.15; }}
h1 {{ font-size: clamp(2rem, 5vw, 3.6rem); font-weight: 700; max-width: 18ch; }}
h2 {{ font-size: clamp(1.3rem, 2.3vw, 1.8rem); font-weight: 600; max-width: 38ch; }}
h3 {{ font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; }}
p {{ margin: 0; max-width: 68ch; }}
.lede {{ font-size: 1.15rem; color: var(--ink-2); max-width: 60ch; }}
.cover .inner {{ gap: 26px; }}
.cover-facts, .facts {{ display: grid; gap: 12px; align-content: start; }}
.cover-facts {{ grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); border-top: 1px solid var(--hair); padding-top: 18px; }}
.cover-facts > div, .facts > div {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
.k {{ font-family: var(--display); font-size: 0.78rem; letter-spacing: {'0.01em' if rtl else '0.06em'}; text-transform: uppercase; color: var(--muted); }}
.v {{ color: var(--ink); }}
.facts > div {{ padding: 10px 0; padding-inline-start: 14px; border-inline-start: 3px solid var(--accent); }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; align-items: start; }}
.cols > div {{ min-width: 0; }}
.chart-cols, .map-cols {{ grid-template-columns: minmax(0, 3fr) minmax(260px, 2fr); }}
@media (max-width: 760px) {{ .chart-cols, .map-cols {{ grid-template-columns: 1fr; }} }}
ul {{ margin: 0; padding: 0; padding-inline-start: 20px; display: flex; flex-direction: column; gap: 8px; }}
ul.tight {{ gap: 5px; font-size: 0.95rem; }}
li {{ max-width: 60ch; }}
.tiles, .recap-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }}
.tile, .recap-grid > div {{ background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 12px 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
.big {{ font-family: var(--display); font-weight: 700; font-size: clamp(1.6rem, 3.5vw, 2.3rem); color: var(--accent-ink); line-height: 1.05; unicode-bidi: plaintext; }}
.lab {{ color: var(--ink-2); font-size: 0.95rem; }}
.steps, .decisions {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }}
.steps {{ grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }}
.steps li, .decisions li {{ display: flex; gap: 12px; align-items: flex-start; background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 14px 16px; min-width: 0; }}
.n {{ flex: none; width: 30px; height: 30px; border-radius: 50%; background: var(--accent); color: #fff; font-family: var(--display); font-weight: 700; display: grid; place-items: center; font-size: 0.95rem; }}
.decisions li > div, .steps li > div {{ max-width: 70ch; }}
.aside {{ color: var(--ink-2); font-size: 0.95rem; border-inline-start: 3px solid var(--hair); padding-inline-start: 12px; }}
.chartbox {{ background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 14px 16px 12px; min-width: 0; }}
.chart {{ width: 100%; height: auto; display: block; font-family: var(--body); direction: ltr; }}
.caption {{ font-size: 0.85rem; color: var(--muted); margin-top: 8px; }}
.source {{ font-size: 0.8rem; color: var(--muted); }}
.mapfig {{ margin: 0; background: #fff; border: 1px solid var(--hair); border-radius: 8px; padding: 8px; min-width: 0; }}
.mapfig img {{ display: block; width: 100%; height: auto; max-width: 100%; border-radius: 4px; }}
.mapfig figcaption {{ font-size: 0.85rem; color: var(--muted); padding: 8px 4px 2px; }}
.fit .good h3 {{ color: var(--good); }} .fit .bad h3 {{ color: var(--bad); }}
.fit > div {{ background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 16px 18px; }}
.keylist {{ list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 0.85rem; color: var(--ink-2); margin-top: 6px; }}
.keylist li {{ display: flex; align-items: center; gap: 6px; }}
.sw {{ width: 12px; height: 12px; border-radius: 2px; display: inline-block; flex: none; }}
.sw.c1 {{ background: var(--accent); }} .sw.c2 {{ background: var(--orange); }} .sw.c3 {{ background: var(--aqua); }}
.sw.o1 {{ background: var(--o1); }} .sw.o2 {{ background: var(--o2); }} .sw.o3 {{ background: var(--o3); }}
/* chart ink */
.chart .grid {{ stroke: var(--grid); stroke-width: 1; }}
.chart .axis {{ stroke: var(--hair); stroke-width: 1; }}
.chart .tick, .chart .legend, .chart .note {{ fill: var(--muted); font-size: 12.5px; }}
.chart .cat {{ fill: var(--ink-2); font-size: 13px; }}
.chart .vlabel {{ fill: var(--ink); font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }}
.chart .vlabel.strong {{ font-size: 13.5px; }}
.chart .share {{ fill: var(--muted); font-weight: 400; }}
.chart .mark.c1 {{ fill: var(--accent); }} .chart .mark.c2 {{ fill: var(--orange); }} .chart .mark.c3 {{ fill: var(--aqua); }}
.chart .mark.o1 {{ fill: var(--o1); }} .chart .mark.o2 {{ fill: var(--o2); }} .chart .mark.o3 {{ fill: var(--o3); }}
.chart .mark.wash {{ fill: var(--wash); }}
.chart .mark-line {{ stroke: var(--accent); stroke-width: 2; stroke-linecap: round; }}
.chart .dot.c1 {{ fill: var(--accent); stroke: var(--surface); stroke-width: 2; }}
.chart .dot.hollow {{ fill: var(--surface); stroke: var(--accent); stroke-width: 2; }}
.chart path.mark:hover {{ opacity: 0.8; }}
/* nav */
.bar {{ position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 16px; padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px)); background: var(--surface); border-top: 1px solid var(--hair); font-size: 0.85rem; color: var(--ink-2); z-index: 5; }}
.bar .title {{ font-family: var(--display); font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }}
.bar .ctl {{ display: flex; align-items: center; gap: 8px; flex: none; }}
.bar button {{ font: inherit; font-weight: 600; color: var(--ink); background: var(--bg); border: 1px solid var(--hair); border-radius: 6px; padding: 5px 12px; cursor: pointer; }}
.bar button:hover {{ border-color: var(--accent); }} .bar button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.bar .count {{ font-variant-numeric: tabular-nums; min-width: 4.5ch; text-align: center; direction: ltr; }}
.progress {{ position: fixed; inset-inline-start: 0; top: env(safe-area-inset-top, 0px); height: 3px; background: var(--accent); width: 0; z-index: 6; transition: width 0.2s; }}
@media (prefers-reduced-motion: reduce) {{ .progress {{ transition: none; }} }}
</style>'''
    # in a right-to-left deck the "forward" arrow key is the left one
    fwd, back = ('ArrowLeft', 'ArrowRight') if rtl else ('ArrowRight', 'ArrowLeft')
    body = f'''<div class="page" dir="{t['dir']}" lang="{t['lang']}">
<div class="progress" id="progress"></div>
<main class="deck" id="deck">
{chr(10).join(slides)}
</main>
<nav class="bar" aria-label="{t['slide_aria']}">
  <span class="title">{t['nav_title']}</span>
  <span class="ctl"><button type="button" id="prev" aria-label="{t['prev_aria']}">{t['prev']}</button><span class="count" id="count">1 / {len(slides)}</span><button type="button" id="next" aria-label="{t['next_aria']}">{t['next']}</button></span>
</nav>
</div>
<script>
(function () {{
  document.documentElement.dir = '{t['dir']}'; document.documentElement.lang = '{t['lang']}';
  var deck = document.getElementById('deck'), slides = Array.prototype.slice.call(deck.querySelectorAll('.slide'));
  var count = document.getElementById('count'), progress = document.getElementById('progress'), cur = 0;
  function show(i) {{ i = Math.max(0, Math.min(slides.length - 1, i)); slides[i].scrollIntoView({{ block: 'start' }}); }}
  function update() {{
    var top = deck.scrollTop, best = 0, bestD = Infinity;
    slides.forEach(function (s, i) {{ var d = Math.abs(s.offsetTop - top); if (d < bestD) {{ bestD = d; best = i; }} }});
    cur = best; count.textContent = (cur + 1) + ' / ' + slides.length; progress.style.width = ((cur + 1) / slides.length * 100) + '%';
    try {{ localStorage.setItem('nofit-deck-slide-{lang}', String(cur)); }} catch (e) {{}}
  }}
  deck.addEventListener('scroll', update, {{ passive: true }});
  document.getElementById('prev').addEventListener('click', function () {{ show(cur - 1); }});
  document.getElementById('next').addEventListener('click', function () {{ show(cur + 1); }});
  document.addEventListener('keydown', function (e) {{
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.key === '{fwd}' || e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {{ e.preventDefault(); show(cur + 1); }}
    else if (e.key === '{back}' || e.key === 'ArrowUp' || e.key === 'PageUp') {{ e.preventDefault(); show(cur - 1); }}
    else if (e.key === 'Home') {{ e.preventDefault(); show(0); }} else if (e.key === 'End') {{ e.preventDefault(); show(slides.length - 1); }}
  }});
  var hash = (location.hash || '').replace('#', ''); var m = /^s(\\d+)$/.exec(hash);
  if (m) {{ show(parseInt(m[1], 10) - 1); }}
  update();
}})();
</script>'''
    return head, body, len(slides)

def main():
    args = sys.argv[1:]
    langs = [args[args.index('--lang') + 1]] if '--lang' in args else ['en', 'he']
    for lang in langs:
        head, body, n = build(lang)
        if '--body-only' in args:
            open(args[args.index('--body-only') + 1], 'w', encoding='utf-8').write(head + '\n' + body + '\n')
        else:
            html = (f'<!doctype html>\n<html lang="{lang}" dir="{S[lang]["dir"]}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                    + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
            open(OUT_HTML[lang], 'w', encoding='utf-8').write(html); print(OUT_HTML[lang], f'{len(html) / 1024:.0f} KB', f'{n} slides')

if __name__ == '__main__': main()
