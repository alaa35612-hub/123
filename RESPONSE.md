# SMC Indicator Extraction Status

## Overview
- **Indicator name:** Smart Money Concept [TradingFinder] Major Minor OB + FVG (SMC)
- **Type:** `indicator` (Pine v5) with overlays, `max_bars_back = 5000`, `max_boxes_count = 500`, `max_labels_count = 500`, `max_lines_count = 500`.
- **Imported libraries:**
  - `TFlab/OrderBlockRefiner_TradingFinder/2` as `Refiner` (OB refinement and price ranges).
  - `TFlab/OrderBlockDrawing_TradingFinder/1` as `Drawing` (zone visualization and alert triggers).
  - `TFlab/FVGDetectorLibrary/1` as `FVG` (fair-value-gap detection/filter).
  - `TFlab/LiquidityFinderLibrary/1` as `Liq` (liquidity lines).
  - `TFlab/AlertSenderLibrary_TradingFinder/1` as `Alert` (alert dispatch). The library logic is not provided, so Python parity is limited.

## Key Inputs (selected)
- Logic: `PP` (pivot period, default 5), `OBVaP` (order block validity period, default 500 bars).
- Display toggles: `ShowDmainCh`, `ShowDsubCh`, `ShowDBoS`, `ShowSmainCh`, `ShowSsubCh`, `ShowSBoS` (all default On).
- Refinement: `RefineDmainCh`, `RefineMeDmainCh`, … `RefineSBoS`, `RefineMeSBoS` (booleans + method strings, default Defensive/on).
- FVG: `PShowDeFVG`, `PShowSuFVG`, `PFVGFilter`, `PFVGFilterType`.
- Liquidity: `ShowSHLL`, `ShowSLLL`, `ShowDHLL`, `ShowDLLL`, `SPP`, `DPP`, `SLLS`, `DLLS`.
- Alerts: `AlertName`, `Alert_DMM/DSM/DAM/SMM/SSM/SAM` with messages for the six required texts; `Frequncy`, `UTC`, `MoreInfo`.
- Numerous line-style inputs exist but are omitted from Python scope since they only affect drawing.

## Alert wiring (from Pine)
- Drawing block produces alert flags via `Drawing.OBDrawing` for each trigger:
  - Demand Main ChoCh → `Alert_DMMM`
  - Demand Sub ChoCh → `Alert_DSMM`
  - Demand BoS → `Alert_DAMM`
  - Supply Main ChoCh → `Alert_SMMM`
  - Supply Sub ChoCh → `Alert_SSMM`
  - Supply BoS → `Alert_SAMM`
- Alert dispatch uses `Alert.AlertSender` combining those flags with enable switches (`Alert_DMM`, `Alert_DSM`, …) and the messages set above.
- Triggers depend on complex ChoCh/BoS detection, zone indexing, and refinement handled by imported libraries and extensive pivot logic inside the script (see `BuMChMain_Trigger`, `BuMChSub_Trigger`, `BuMBoS_Trigger`, `BeMChMain_Trigger`, `BeMChSub_Trigger`, `BeMBoS_Trigger`).

## Current Python status
- Added `smc_scanner.py` as a runnable scaffold using `ccxt` to pull Binance USDT-M futures data and mirror indicator inputs as configuration variables.
- Detection logic is stubbed (`detect_zones_and_signals` returns no signals) because the Pine code relies on proprietary libraries whose implementations are unavailable. Once library logic is ported, integrate ChoCh/BoS detection, order block creation, refinement, FVG/liquidity filters, and alert gating.

## Limitations
- No attempt was made to reimplement zigzag/major/minor pivot logic or zone math because the full Pine logic spans numerous dependent blocks beyond the available time and depends on imported libraries.
- Alert texts and enable switches are preserved; the Python scaffold is structured to emit the six requested messages once detection code is supplied.
