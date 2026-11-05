# The Metronit scenario: the Metronit kept on the Krayot side of Merkazit Hamifrats only — 2040 / 2050 × BU / HS

**5 November 2026.** Step 45 rerun with `METRONIT_CUT="BU_2040,BU_2050,HS_2040,HS_2050"` (pipeline step `v45_metro`, METHODOLOGY §6aq addendum 5), output `Output/alternatives_metronit_krayot/`. Every number here is read from that folder and from the central run (`Output/alternatives/`) by `tools/metronit_scenario_summary.py`, which also writes the comparison tables and the charts named below. Three-hour periods unless the peak hour is named.

## 1. The scenario

Once the LRT runs, the Metronit serves the Krayot only, up to Merkazit Hamifrats; in Haifa and Tirat Carmel the LRT is the one mass-transit mode beside the train and the buses. In the model: every Metronit ride edge with a stop in Haifa proper or Tirat Carmel (the zonal superzones 13–17 and 24 — the Carmel coast and Hof HaCarmel, Bat Galim and Kiryat Eliezer, the lower city, Hadar, the Check Post / Gesher Paz, Tirat Carmel) is removed from the transit graph of the four forecast sets; the edges between the Krayot, Kiryat Haim, the Hamifrats bay zone (Merkazit Hamifrats, Lev Hamifrats, the refineries, Tsomet Kiryat Ata), Nesher and Yagur stay. Lines 1 and its limited-stop twin run Merkazit Hamifrats ↔ Merkazit HaKrayot, line 3 Merkazit Hamifrats ↔ Kiryat Ata, line 2 keeps its Krayot ↔ Hamifrats legs and loses its Hadar loop, the Yagur – Nesher line ends at Nesher. Of the 170 Metronit stops 97 stay and 73 go. The buses (every line as it runs today), the train, the car and the LRT (through line, main route + extension, 5-minute headway) are as in the central case; the 2022 base keeps today's network.

The pivot measures the transit nest's change from **today's** network: a pair that gains the LRT moves trips from the car as before; a pair that loses its Metronit without an LRT worth the change loses transit share to the car. The LRT's share within transit is taken against the scenario's best no-LRT path, so where the Metronit is gone the LRT competes with the bus alone and carries the bus premium (5 generalized minutes) rather than the Metronit's (2.5). Without a cut the formula is step 31's exactly: the 2022 rows of the scenario run reproduce the central run to 0.0 trips.

## 2. The headline: LRT trips, main route + extension, Prioritized

| period | scenario-year | LRT central | LRT scenario | change | using the extension, central | using the extension, scenario | from car, central | from car, scenario | busiest segment (3 h), central | busiest segment (3 h), scenario |
|---|---|---|---|---|---|---|---|---|---|---|
| AM | 2040 BU | 6,309 | 8,214 | +30 % | 4,950 | 6,854 | 353 | 128 | 2,114 | 3,173 |
| AM | 2050 BU | 7,433 | 9,570 | +29 % | 6,003 | 8,141 | 818 | 567 | 2,345 | 3,552 |
| AM | 2040 HS | 7,476 | 9,416 | +26 % | 5,651 | 7,590 | 870 | 672 | 2,509 | 3,570 |
| AM | 2050 HS | 9,225 | 11,479 | +24 % | 7,010 | 9,265 | 1,311 | 1,103 | 3,058 | 4,286 |
| PM | 2040 BU | 5,358 | 7,022 | +31 % | 4,300 | 5,964 | 327 | 170 | 1,284 | 2,017 |
| PM | 2050 BU | 6,135 | 8,031 | +31 % | 4,998 | 6,894 | 368 | 199 | 1,684 | 2,226 |
| PM | 2040 HS | 5,620 | 7,304 | +30 % | 4,595 | 6,280 | 425 | 265 | 1,407 | 2,225 |
| PM | 2050 HS | 5,956 | 7,777 | +31 % | 4,918 | 6,739 | 466 | 296 | 1,398 | 2,271 |

Peak hour (the survey's factors, AM 0.59 / PM 0.48 of the three hours; the upper reading, caveat 18): 2050 BU AM 5,637 LRT trips against 4,378 in the central case; PM 3,840 against 2,934.

## 3. Where the trips come from and where the Metronit riders go

| scenario-year | corridor Metronit riders today | Metronit riders after, central | Metronit riders after, scenario | bus riders after, central | bus riders after, scenario | car → transit, central | car → transit, scenario | pairs with transit dearer than today | their transit trips today | of which lost to the car | of which on the LRT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2040 BU | 10,000 | 6,863 | 3,170 | 5,832 | 7,208 | 684 | 271 | 2,150 | 2,558 | 278 | 1,689 |
| 2050 BU | 11,282 | 7,816 | 3,637 | 6,824 | 8,338 | 1,421 | 893 | 2,150 | 2,829 | 320 | 1,865 |
| 2040 HS | 10,496 | 6,992 | 3,025 | 5,707 | 7,311 | 1,387 | 964 | 2,230 | 2,366 | 264 | 1,538 |
| 2050 HS | 12,102 | 7,908 | 3,229 | 6,135 | 8,061 | 2,035 | 1,537 | 2,230 | 2,594 | 287 | 1,681 |

Sources of the LRT trips, AM 2050 BU (the source is the pair's path type today: Metronit-based, bus-based, or the car):

| source | central | scenario | difference |
|---|---|---|---|
| from Metronit-based pairs | 3,731 | 6,008 | 2,277 |
| from bus-based pairs | 2,881 | 2,993 | 111 |
| from the car | 817 | 567 | -251 |

## 4. The markets of the LRT trips, AM

| scenario-year | market | LRT central | LRT scenario | difference | ratio |
|---|---|---|---|---|---|
| 2050 BU | Tirat Carmel ↔ Haifa | 2,189 | 2,367 | 178 | 1.08 |
| 2050 BU | Haifa internal | 1,663 | 2,132 | 469 | 1.28 |
| 2050 BU | Krayot ↔ Haifa (by feeder) | 1,665 | 2,753 | 1,088 | 1.65 |
| 2050 BU | Main route ↔ Haifa | 891 | 1,091 | 200 | 1.22 |
| 2050 BU | Main route ↔ Krayot / Tirat Carmel | 522 | 559 | 37 | 1.07 |
| 2050 BU | within the main route | 306 | 306 | 0 | 1.00 |
| 2050 BU | Krayot ↔ Tirat Carmel | 193 | 358 | 165 | 1.85 |
| 2050 BU | total | 7,432 | 9,569 | 2,137 | 1.29 |
| 2050 HS | Tirat Carmel ↔ Haifa | 1,041 | 1,116 | 76 | 1.07 |
| 2050 HS | Haifa internal | 3,027 | 3,660 | 632 | 1.21 |
| 2050 HS | Krayot ↔ Haifa (by feeder) | 2,030 | 3,201 | 1,171 | 1.58 |
| 2050 HS | Main route ↔ Haifa | 1,533 | 1,811 | 278 | 1.18 |
| 2050 HS | Main route ↔ Krayot / Tirat Carmel | 846 | 863 | 17 | 1.02 |
| 2050 HS | within the main route | 639 | 639 | 0 | 1.00 |
| 2050 HS | Krayot ↔ Tirat Carmel | 105 | 183 | 78 | 1.75 |
| 2050 HS | total | 9,225 | 11,478 | 2,253 | 1.24 |

The full table for the four scenario-years is `markets_vs_central_AM.csv`.

## 5. Line loads and stations

| period | scenario-year | direction | busiest segment, central | peak-hour load, central | busiest segment, scenario | peak-hour load, scenario | busiest extension segment, scenario | its peak-hour load |
|---|---|---|---|---|---|---|---|---|
| AM | 2040 BU | to Tirat Carmel | S24–M02 | 966 | S24–M02 | 1,450 | S23–S24 | 1,300 |
| AM | 2040 BU | to Nazareth | S14–S15 | 765 | S14–S15 | 990 | S14–S15 | 990 |
| AM | 2050 BU | to Tirat Carmel | S24–M02 | 1,071 | S24–M02 | 1,623 | S23–S24 | 1,466 |
| AM | 2050 BU | to Nazareth | S14–S15 | 1,028 | S14–S15 | 1,284 | S14–S15 | 1,284 |
| AM | 2040 HS | to Tirat Carmel | S24–M02 | 1,146 | S24–M02 | 1,631 | S23–S24 | 1,468 |
| AM | 2040 HS | to Nazareth | S14–S15 | 830 | S14–S15 | 1,053 | S14–S15 | 1,053 |
| AM | 2050 HS | to Tirat Carmel | S24–M02 | 1,397 | S24–M02 | 1,958 | S23–S24 | 1,773 |
| AM | 2050 HS | to Nazareth | S14–S15 | 1,054 | S14–S15 | 1,311 | S14–S15 | 1,311 |
| PM | 2040 BU | to Tirat Carmel | S05–S06 | 579 | S12–S13 | 742 | S12–S13 | 742 |
| PM | 2040 BU | to Nazareth | S24–M02 | 687 | S24–M02 | 1,079 | S23–S24 | 1,069 |
| PM | 2050 BU | to Tirat Carmel | S05–S06 | 787 | S05–S06 | 922 | S05–S06 | 922 |
| PM | 2050 BU | to Nazareth | S24–M02 | 747 | S24–M02 | 1,191 | S23–S24 | 1,175 |
| PM | 2040 HS | to Tirat Carmel | S11–S12 | 501 | S14–S15 | 671 | S14–S15 | 671 |
| PM | 2040 HS | to Nazareth | S24–M02 | 753 | S23–S24 | 1,190 | S23–S24 | 1,190 |
| PM | 2050 HS | to Tirat Carmel | S11–S12 | 536 | S14–S15 | 721 | S14–S15 | 721 |
| PM | 2050 HS | to Nazareth | S24–M02 | 748 | S23–S24 | 1,215 | S23–S24 | 1,215 |

Stations with the largest gain of boardings + alightings, AM 2050 BU:

| station | area | boardings central | boardings scenario | alightings central | alightings scenario | gain |
|---|---|---|---|---|---|---|
| M02 | Bazan-Hutsot | 1,893 | 2,997 | 594 | 803 | 1,313 |
| S06 | Matam-NeotPeres | 143 | 209 | 830 | 1,141 | 378 |
| S19 | LowerCity | 94 | 131 | 616 | 945 | 366 |
| S16 | BatGalim-KiryatEliezer | 273 | 350 | 683 | 874 | 266 |
| S21 | Namal-Giborim | 210 | 283 | 374 | 556 | 255 |
| S24 | Hamifrats | 242 | 354 | 864 | 980 | 227 |
| S17 | Hamoshava | 202 | 261 | 314 | 458 | 203 |
| S18 | Hamoshava | 111 | 143 | 387 | 547 | 192 |

## 6. The other alternative and regime

| period | scenario-year | alternative | regime | LRT central | LRT scenario | change |
|---|---|---|---|---|---|---|
| AM | 2040 BU | Main route + extension | Prioritized | 6,309 | 8,214 | +30 % |
| AM | 2040 BU | Main route + extension | Unprioritized | 4,999 | 6,774 | +35 % |
| AM | 2040 BU | Extension only | Prioritized | 4,879 | 6,472 | +33 % |
| AM | 2040 BU | Extension only | Unprioritized | 3,595 | 5,016 | +40 % |
| AM | 2050 BU | Main route + extension | Prioritized | 7,433 | 9,570 | +29 % |
| AM | 2050 BU | Main route + extension | Unprioritized | 5,700 | 7,672 | +35 % |
| AM | 2050 BU | Extension only | Prioritized | 5,939 | 7,714 | +30 % |
| AM | 2050 BU | Extension only | Unprioritized | 4,242 | 5,815 | +37 % |
| AM | 2040 HS | Main route + extension | Prioritized | 7,476 | 9,416 | +26 % |
| AM | 2040 HS | Main route + extension | Unprioritized | 6,010 | 7,835 | +30 % |
| AM | 2040 HS | Extension only | Prioritized | 5,424 | 7,026 | +30 % |
| AM | 2040 HS | Extension only | Unprioritized | 4,008 | 5,441 | +36 % |
| AM | 2050 HS | Main route + extension | Prioritized | 9,225 | 11,479 | +24 % |
| AM | 2050 HS | Main route + extension | Unprioritized | 7,393 | 9,527 | +29 % |
| AM | 2050 HS | Extension only | Prioritized | 6,653 | 8,538 | +28 % |
| AM | 2050 HS | Extension only | Unprioritized | 4,893 | 6,593 | +35 % |
| PM | 2040 BU | Main route + extension | Prioritized | 5,358 | 7,022 | +31 % |
| PM | 2040 BU | Main route + extension | Unprioritized | 4,263 | 5,832 | +37 % |
| PM | 2040 BU | Extension only | Prioritized | 4,270 | 5,711 | +34 % |
| PM | 2040 BU | Extension only | Unprioritized | 3,193 | 4,508 | +41 % |
| PM | 2050 BU | Main route + extension | Prioritized | 6,135 | 8,031 | +31 % |
| PM | 2050 BU | Main route + extension | Unprioritized | 4,854 | 6,659 | +37 % |
| PM | 2050 BU | Extension only | Prioritized | 4,960 | 6,619 | +33 % |
| PM | 2050 BU | Extension only | Unprioritized | 3,700 | 5,230 | +41 % |
| PM | 2040 HS | Main route + extension | Prioritized | 5,620 | 7,304 | +30 % |
| PM | 2040 HS | Main route + extension | Unprioritized | 4,512 | 6,126 | +36 % |
| PM | 2040 HS | Extension only | Prioritized | 4,608 | 6,034 | +31 % |
| PM | 2040 HS | Extension only | Unprioritized | 3,516 | 4,840 | +38 % |
| PM | 2050 HS | Main route + extension | Prioritized | 5,956 | 7,777 | +31 % |
| PM | 2050 HS | Main route + extension | Unprioritized | 4,768 | 6,523 | +37 % |
| PM | 2050 HS | Extension only | Prioritized | 4,918 | 6,487 | +32 % |
| PM | 2050 HS | Extension only | Unprioritized | 3,748 | 5,216 | +39 % |

## 7. Charts

- `Output/alternatives_metronit_krayot/figures/line_loads_vs_central_AM_BU_2050_to_Nazareth.png`
- `Output/alternatives_metronit_krayot/figures/line_loads_vs_central_AM_BU_2050_to_Tirat_Carmel.png`
- `Output/alternatives_metronit_krayot/figures/line_loads_vs_central_PM_BU_2050_to_Nazareth.png`
- `Output/alternatives_metronit_krayot/figures/line_loads_vs_central_PM_BU_2050_to_Tirat_Carmel.png`
- `Output/alternatives_metronit_krayot/figures/lrt_alternatives_demand.png`
- `Output/alternatives_metronit_krayot/figures/lrt_alternatives_line_loads.png`
- `Output/alternatives_metronit_krayot/figures/lrt_alternatives_lines.png`
- `Output/alternatives_metronit_krayot/figures/lrt_trips_vs_central_AM.png`
- `Output/alternatives_metronit_krayot/figures/lrt_trips_vs_central_PM.png`
- `Output/alternatives_metronit_krayot/figures/mode_change_vs_central_AM.png`

## 8. How to read it

- The scenario is a **network decision**, not a demand uncertainty: the comprehensive report's section 4.4 anticipated that a reduced Metronit would raise the LRT's trunk loads by up to the Metronit's corridor volume. This run puts a number on it with the model's own choice mechanism; the comprehensive report carries it as section 4.10.
- The cut reads the superzone of each stop's TAZ from `Zonal_2020.csv` (`SZ_NEW`). Caveat 19 notes that this column disagrees with the chain's key table in 142 TAZs; 18 of the 60 TAZs with a Metronit stop are among them, every one on the same side of the cut under either key, so the partition of the 170 stops is the same.
- What is not modelled: no bus restructuring beside the cut (the buses parallel to the Metronit's former Haifa section keep running, so the no-LRT alternative in Haifa is the bus, not nothing), no capacity on the LRT or at Merkazit Hamifrats, no change of Metronit frequencies, no fare, no park-and-ride. The λ, the out-of-vehicle weights, the peak-hour factor and the aggregation dependence of the pivot (caveats 15, 18, 27, 33) apply as in the central case; the planning range of the central case (λ 0.02–0.05) scales this scenario the same way.
- The transit lost to the car is the pivot's reading of the pairs whose Metronit is gone and whose LRT path is dearer than today's Metronit path (long walks to a station, a feeder transfer); it is small against the market and is an upper reading, since those riders would in practice also find restructured buses.
