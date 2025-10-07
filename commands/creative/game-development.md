---
name: game-development
description: Complete game development workflow coordinating game-designer, narrative-designer, music-composer, sound-designer, and digital-artist for indie or AA game production
---

# Game Development

## Overview

This command orchestrates a comprehensive game development workflow from concept to playable build. It coordinates game design, narrative systems, audio production, and visual assets to produce a professional game project ready for player testing or release.

**What this accomplishes:**
- Complete game design document with mechanics, progression, and balance systems
- Interactive narrative with branching dialogue, quest systems, and world-building lore
- Adaptive music system synchronized to gameplay states and emotional beats
- Comprehensive sound design with SFX, UI audio, ambiences, and spatial 3D audio
- Production-ready visual assets including UI, characters, environments, and marketing art

**When to use:**
- Indie game projects (narrative-driven, RPG, adventure, puzzle)
- Game jam prototypes transitioning to full development
- Early access or Kickstarter game pitches
- AA game production requiring professional creative direction

**Expected outcomes:**
- Playable prototype with complete creative assets
- Game design documentation for full team implementation
- Interactive story with meaningful player choices
- Immersive audio-visual experience

**Estimated execution time:** 8-16 weeks for vertical slice or demo build

## Multi-Agent Orchestration Strategy

### **Phase 1: Game Design Foundation**
Deploy `game-designer` to:
- Create comprehensive game design document (GDD) with core mechanics, gameplay loop, and progression
- Design level architecture, spatial layouts, enemy placement, and difficulty curves
- Develop player psychology hooks (flow state, retention mechanics, skill expression)
- Create technical specifications for implementation (data structures, algorithms, edge cases)
- Deliver playtested prototype demonstrating core gameplay loop

**Why this agent:** Game-designer specializes in gameplay mechanics, level design, player experience, and game balance. Provides structural foundation for all other creative work.

### **Phase 2: Interactive Narrative**
Engage `narrative-designer` to:
- Build branching narrative system with dialogue trees, story flags, and player choice architecture
- Create world-building lore (history, cultures, factions, mythology) delivered through environmental storytelling
- Design quest structures with multiple solutions (stealth, combat, social, puzzle approaches)
- Implement relationship systems tracking NPC approval, faction reputation, and story consequences
- Deliver narrative database (ink/Yarn scripts) integrated with game systems

**Why this agent:** Narrative-designer creates interactive stories with meaningful player agency, distinct from screenwriter (linear narrative) and game-designer (mechanical systems).

**Handoff:** GDD defines gameplay mechanics and player verbs. Narrative-designer creates story systems utilizing those mechanics for player-driven storytelling.

### **Phase 3: Audio Production**
Coordinate parallel audio development:

#### **Phase 3a: Music Composition**
Use `music-composer` to:
- Design adaptive music system with vertical layers (intensity-driven) and horizontal sequences (location-based)
- Compose main theme, character leitmotifs, and location-specific tracks
- Create seamless looping music with transition stingers and exploration/combat variations
- Deliver FMOD or Wwise implementation with parameter-driven adaptive systems
- Provide music stems for dynamic mixing based on gameplay state

**Why this agent:** Music-composer creates original scores with thematic development, adaptive game music systems, and FMOD/Wwise implementation expertise.

#### **Phase 3b: Sound Design**
Deploy `sound-designer` to:
- Create complete SFX library for player actions (attacks, abilities, movement, UI interactions)
- Design environmental ambiences and soundscapes for each location
- Implement 3D spatial audio with distance attenuation, occlusion, and reverb zones
- Produce foley for character animations and physics interactions
- Deliver middleware project (FMOD/Wwise) with randomization, parameter controls, and performance optimization

**Why this agent:** Sound-designer specializes in sound effects creation, foley, spatial audio, and game audio middleware implementation.

**Parallel Execution:** Music and sound design can proceed simultaneously after gameplay mechanics and narrative locations are defined. Both coordinate on sonic territory (frequency ranges, emotional spaces).

### **Phase 4: Visual Asset Production**
Engage `digital-artist` to:
- Design UI/UX system (menus, HUD, inventory, dialogue boxes) with consistent visual language
- Create character sprites or concept art (depending on art style: pixel, 2D, 3D concept)
- Develop environmental assets (tilesets, backgrounds, props) supporting level design
- Produce marketing assets (key art, Steam capsule, promotional illustrations)
- Deliver production-ready assets optimized for target platform (resolution, file format, texture atlases)

**Why this agent:** Digital-artist creates visual assets for games including UI, sprites, environments, and marketing materials. Integrates with game-designer's level layouts and narrative-designer's world-building.

**Handoff:** Level designs and narrative locations define visual requirements. Digital-artist creates assets matching spatial needs and thematic tone.

### **Phase 5: Integration & Polish**
Coordinate `project-orchestrator` to:
- Integrate all creative assets into playable build (Unity, Unreal, Godot, or custom engine)
- Ensure narrative choices, audio cues, and visual elements trigger correctly based on game state
- Balance audio mixing (dialogue intelligibility, music supporting not overwhelming, SFX clarity)
- Conduct playtesting sessions tracking player engagement, confusion points, and emotional responses
- Polish based on feedback (adjust difficulty, clarify mechanics, fix narrative bugs, balance audio)

**Why this agent:** Project-orchestrator manages cross-discipline integration, prevents creative silos, and delivers cohesive player experience.

## Execution Flow

```
Phase 1: Game Design Foundation (game-designer)
    ↓ [GDD complete, core loop prototyped]
Phase 2: Interactive Narrative (narrative-designer)
    ↓ [Story systems, quest DB, lore delivered]
Phase 3a: Music Composition (music-composer)  ┐
                                              ├→ Audio Integration
Phase 3b: Sound Design (sound-designer)       ┘
    ↓ [FMOD/Wwise project with all audio]
Phase 4: Visual Assets (digital-artist)
    ↓ [UI, characters, environments delivered]
Phase 5: Integration & Polish (project-orchestrator)
    ↓
[Playable build ready for testing or early access]
```

## Expected Deliverables

- **Game Design Document**: Comprehensive GDD with mechanics, progression, balance (Markdown/Google Docs, 20-50 pages)
- **Technical Specifications**: Data structures, algorithms, edge case handling for implementation (PDF/Notion)
- **Level Designs**: Spatial layouts, enemy placement, item locations (diagrams, Tiled maps, or engine files)
- **Narrative Database**: Dialogue trees, quest structures, story flags (ink/Yarn scripts, JSON database)
- **World Lore Bible**: History, factions, cultures, mythology (Markdown/Wiki, 30-100 pages for deep lore)
- **Adaptive Music System**: FMOD/Wwise project with layered music, transitions, parameters (middleware project + WAV stems)
- **Sound Effects Library**: Complete SFX for player actions, UI, environment (WAV 48kHz, organized folders, ~200-500 sounds)
- **3D Audio Implementation**: Spatial audio with distance curves, reverb zones, occlusion (middleware configuration)
- **Visual Assets**: UI components, character art, environmental assets, marketing art (PNG/PSD, optimized for engine)
- **Playable Build**: Integrated game demonstrating core loop, story sample, audio-visual quality (EXE/APK/Web build)

## Success Criteria

- [ ] Core gameplay loop is fun and engaging based on playtesting feedback (>7/10 fun score)
- [ ] Player choices have meaningful consequences visible in narrative outcomes
- [ ] Adaptive music responds smoothly to gameplay state changes without audio pops
- [ ] Sound effects enhance game feel (hits feel impactful, UI responsive, environment immersive)
- [ ] Visual assets are cohesive with consistent art style and readable at target resolution
- [ ] Game runs at stable 60fps (or 30fps for mobile) on target hardware
- [ ] Tutorial/onboarding successfully teaches mechanics without frustrating players
- [ ] Narrative coherence: branching paths don't create plot holes or contradictions
- [ ] Audio mix balanced: dialogue clear, music supports without overpowering, SFX impactful
- [ ] Vertical slice or demo build represents final game quality and vision

## Common Issues and Solutions

**Issue:** Game design too ambitious for team size/timeline
**Solution:** Game-designer reduces scope to core loop, cuts secondary systems for post-launch
**Prevention:** Define MVP (minimum viable product) early, prioritize ruthlessly

**Issue:** Narrative branches exponentially, unsustainable content volume
**Solution:** Narrative-designer uses convergent branching (choices reunite at critical path) and systemic reactivity (flags change dialogue, not entire paths)
**Prevention:** Scope branching early, use hub-and-spoke structure instead of exponential tree

**Issue:** Adaptive music transitions sound abrupt or jarring
**Solution:** Music-composer adds crossfade transitions, uses musical cues to signal changes
**Prevention:** Test transitions early in development, iterate based on gameplay feel

**Issue:** Sound effects repetitive (same footstep sound 100 times)
**Solution:** Sound-designer implements randomization (pitch, volume, sample variation) in middleware
**Prevention:** Design for variation from start, record multiple takes of each sound

**Issue:** Visual assets don't match game design level layouts
**Solution:** Digital-artist revises based on updated level designs, iterative feedback loop
**Prevention:** Establish asset specifications early (tile size, resolution, style guide), regular check-ins

**Issue:** Game performs poorly with all audio-visual assets integrated
**Solution:** Optimize assets (compress textures, reduce poly counts), optimize audio (streaming vs memory, voice limiting)
**Prevention:** Set performance budgets early, profile regularly during development

## Related Commands

- **`/development:game-prototype`**: Rapid prototyping focused on core mechanics without full production assets
- **`/creative:narrative-systems`**: Deep dive into interactive storytelling without mechanical gameplay focus
- **`/quality:playtesting-analysis`**: Structured playtesting sessions with metric tracking and feedback analysis
- **`/creative:music-composition`**: Standalone music composition without game integration

## Notes

**Genre-Specific Adaptations:**
- **RPG**: Heavy emphasis on narrative-designer (branching quests, choice consequences) and game-designer (progression systems, stat balancing)
- **Action/Platformer**: Prioritize game-designer (level design, movement feel) and sound-designer (impactful SFX, responsive audio feedback)
- **Puzzle**: Game-designer leads (mechanic elegance, difficulty curve), minimal music (ambient, non-intrusive)
- **Horror**: Sound-designer and music-composer critical (tension building, jump scares), narrative-designer for atmospheric storytelling
- **Narrative Adventure**: Narrative-designer leads, game-designer ensures mechanics support story (walking sim, choice-driven)

**Engine-Specific Considerations:**
- **Unity**: FMOD or Wwise integration, C# scripting, asset pipeline via Asset Store
- **Unreal**: Blueprints + C++, MetaSounds for audio, marketplace assets
- **Godot**: GDScript, built-in audio system (less sophisticated than FMOD/Wwise), open-source friendly
- **Custom Engine**: Higher development cost, full control, requires audio middleware integration from scratch

**Platform Optimization:**
- **PC**: Higher quality assets, less aggressive optimization, flexibility
- **Mobile**: Aggressive asset compression, touch UI design, battery/data considerations
- **Console**: Platform-specific certification requirements, controller-optimized UI, consistent frame rate critical
- **Web**: File size constraints, WebGL limitations, accessibility important

**Monetization Models:**
- **Premium ($10-$30)**: Full game upfront, no IAP, all content included
- **Free-to-Play + IAP**: Cosmetics, time-savers, or additional content purchasable
- **Early Access**: Partial game released, iterate based on player feedback, full release later
- **Crowdfunding**: Kickstarter/Patreon for indie funding, community-driven development

**Timeline Estimates:**
- **Game Jam (48-72 hours)**: Minimal scope, core loop only, rough assets
- **Vertical Slice (2-4 months)**: Polished sample demonstrating final quality
- **Demo/Early Access (6-12 months)**: 2-5 hours of gameplay, representative of full game
- **Full Indie Game (1-3 years)**: 10-40 hours of content depending on genre and team size

This workflow ensures professional game development through coordinated specialist expertise from design to playable build.
