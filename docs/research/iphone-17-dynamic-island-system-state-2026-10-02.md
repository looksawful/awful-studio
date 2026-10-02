# iPhone 17 Dynamic Island system-state behavior — 2026-10-02

## Question

When should the black Dynamic Island be present, change shape, split, or disappear on iPhone 17, and how should that affect a 3D/web mockup that swaps arbitrary Home Screen, app, and website textures?

## Primary-source findings

### Dynamic Island is a system layer above apps

Apple Support states that on supported models Dynamic Island appears at the top of the Home Screen or the active app, and that it appears at the top of the screen whenever the iPhone is unlocked.

Primary source:
- Apple Support — View Live Activities in the Dynamic Island on iPhone
  https://support.apple.com/en-euro/guide/iphone/iph28f50d10d/ios

Apple's WWDC23 design session describes Dynamic Island as:
- a blend of hardware and software;
- a singular system layer that shape-shifts;
- a surface that floats on a layer above apps;
- something apps should not draw UI that points to or interacts with directly.

Primary source:
- Apple Developer — Design dynamic Live Activities, WWDC23
  https://developer.apple.com/videos/play/wwdc2023/10194/

**Implication:** an app/site bitmap must not own the baseline black Dynamic Island. Replacing Home Screen artwork with a white website must not expose only the two physical apertures.

### Dynamic Island does not become “nothing” when there is no Live Activity

Apple documents that when a Live Activity ends, that Live Activity is immediately removed from Dynamic Island. This is about the activity presentation, not removing the Dynamic Island system/hardware region itself.

Primary source:
- Apple Human Interface Guidelines — Live Activities
  https://developer.apple.com/design/human-interface-guidelines/live-activities

Apple Support separately says Dynamic Island appears whenever the iPhone is unlocked.

**Implication:** the state “no Live Activity” should return to a baseline/idle Dynamic Island, not to “no island”.

### One Live Activity uses the compact presentation

Apple ActivityKit documentation says that when one Live Activity is active, the system uses the compact presentation. It has separate leading and trailing views around the TrueDepth camera, but they form one cohesive Dynamic Island presentation.

Primary source:
- Apple Developer — Displaying live data with Live Activities
  https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities

Apple's HIG says compact leading/trailing content should be snug against the TrueDepth camera and read as unified information.

Primary source:
- Apple HIG — Live Activities
  https://developer.apple.com/design/human-interface-guidelines/live-activities

### Multiple Live Activities can produce an attached + detached split state

Apple documents that when multiple Live Activities from different apps are active, the system uses minimal presentations. One appears attached to Dynamic Island while another appears detached; the detached view can be circular or oval.

Primary sources:
- Apple HIG — Live Activities
  https://developer.apple.com/design/human-interface-guidelines/live-activities
- Apple Developer — Displaying live data with Live Activities
  https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities

**Implication:** a visibly split two-bubble state is legitimate, but it is a special multi-activity state, not the default appearance of Safari or a normal app.

### Expanded presentation is a larger system container around TrueDepth

Apple documents an expanded Dynamic Island presentation for alerts and interaction. It wraps content around the TrueDepth region.

For iPhone 17, the current HIG gives:
- compact/minimal Dynamic Island width: 230 pt;
- expanded width: 371 pt;
- Dynamic Island corner radius: 44 pt.

Primary source:
- Apple HIG — Live Activities
  https://developer.apple.com/design/human-interface-guidelines/live-activities

Important limitation: these numbers are Live Activity presentation guidance, not evidence for the exact idle/base island-mask dimensions.

### Privacy dots are conditional indicators, not permanent artwork

Apple Support documents:
- orange indicator: microphone in use;
- green indicator: camera, or camera + microphone, in use.

Primary source:
- Apple Support — About the orange and green indicators in your iPhone status bar
  https://support.apple.com/ru-ru/108331

**Implication:** the orange dot must not be baked permanently into normal Home Screen or website artwork.

### iPhone 17 officially includes Dynamic Island

Apple's iPhone 17 technical specifications list:
- 1206 × 2622 OLED display;
- Dynamic Island as a display feature.

Primary source:
- Apple — iPhone 17 Technical Specifications
  https://www.apple.com/de/iphone-17/specs/

## Recommended state model for the mockup

This is a modeling recommendation derived from the Apple sources above, not an Apple API specification.

### 1. idle

Use for:
- unlocked Home Screen;
- Safari / website;
- ordinary app with no island activity.

Render:
- arbitrary app/site texture;
- baseline black Dynamic Island system mask above it;
- physical under-glass sensor pill + camera aperture remain aligned underneath;
- no privacy dot by default.

This is the state the current white-site preview needs.

### 2. privacy_mic

Baseline island + orange microphone indicator.

### 3. privacy_camera

Baseline island + green camera indicator.

### 4. compact_activity

One Live Activity. Dynamic Island reshapes/extends around the sensor region and displays compact leading/trailing content on the black system background.

### 5. minimal_multi_activity

Multiple activities. Permit one minimal presentation attached to Dynamic Island and one detached circular/oval presentation.

### 6. expanded_activity

Large expanded black system container around/under the TrueDepth region.

### 7. transient system alerts

Face ID, AirDrop, calls, recording, timers and similar system experiences can shape-shift the island. Apple does not publish a complete pixel-by-pixel state machine for every transition, so the mockup should model stable states first rather than invent intermediate frames.

## Architecture implication for the current iPhone 17 asset

The current architecture is wrong if the outer black island exists only inside a specific screen raster.

Current failure:
- Home Screen texture contains an outer black island;
- white site texture does not;
- runtime then exposes only the two physical black hardware apertures.

Recommended compositing contract:

1. `SCREEN_CONTENT`: arbitrary replaceable Home Screen / app / website image.
2. `DYNAMIC_ISLAND_SYSTEM_MASK`: system-owned OLED-black state independent of app artwork.
3. Optional system-state content: orange/green privacy indicator, compact/minimal/expanded Live Activity graphics, transient alert graphics.
4. Physical `FRONT_SENSOR_MASK`, `FRONT_CAMERA_MASK`, and optic stack remain physical under-glass geometry.
5. Prefer doing the system mask in the screen material/compositing path rather than a coplanar overlay mesh, so the previous z-fighting problem does not return.

## What should change later in implementation

- Replacing screen artwork must never implicitly remove the baseline idle island.
- `set screen = website` should preserve an explicit `DynamicIslandState.idle` unless another system state is selected.
- Orange privacy indicator should become conditional, not part of the default raster.
- Current hardware datum, front cutouts, cover-glass relationship, and recessed camera stack should remain untouched.

## Suggested test seams for implementation

1. **Screen-state independence**
   - replace Home Screen with a white/site raster;
   - baseline island remains present and aligned.

2. **Privacy-state conditionality**
   - idle: no orange/green indicator;
   - mic: orange;
   - camera: green.

3. **Live Activity state**
   - compact/minimal/expanded are system states, not alternate app bitmaps.

4. **No geometry regression**
   - front hardware/camera depth unchanged;
   - no new coplanar overlay geometry.

5. **Replaceable screen contract**
   - arbitrary imported screen textures are not required to contain Dynamic Island artwork.

## Uncertainties / do not overclaim

- Apple does not publish every intermediate Dynamic Island animation frame.
- The HIG's 230 pt / 371 pt values describe Live Activity presentations, not the exact idle mask.
- Apple does not document a developer-controlled ordinary-app state that hides Dynamic Island while unlocked.
- Screenshot capture behavior is not specified in the primary sources reviewed here, so whether a screenshot file contains the island must not be used as evidence for physical-device appearance.

## Primary sources

1. Apple Support — View Live Activities in the Dynamic Island on iPhone
   https://support.apple.com/en-euro/guide/iphone/iph28f50d10d/ios
2. Apple Developer — Design dynamic Live Activities (WWDC23)
   https://developer.apple.com/videos/play/wwdc2023/10194/
3. Apple Human Interface Guidelines — Live Activities
   https://developer.apple.com/design/human-interface-guidelines/live-activities
4. Apple Developer — Displaying live data with Live Activities
   https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities
5. Apple Support — About the orange and green indicators in your iPhone status bar
   https://support.apple.com/ru-ru/108331
6. Apple — iPhone 17 Technical Specifications
   https://www.apple.com/de/iphone-17/specs/
7. Apple Newsroom — iPhone 14 Pro introduction / Dynamic Island overview
   https://www.apple.com/de/newsroom/2022/09/apple-debuts-iphone-14-pro-and-iphone-14-pro-max/
