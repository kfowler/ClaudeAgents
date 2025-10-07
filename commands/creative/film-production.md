---
name: film-production
description: Complete film production workflow coordinating screenwriter, cinematographer, sound-designer, and music-composer for professional short or feature film development
---

# Film Production

## Overview

This command orchestrates a complete film production workflow from script to final audio-visual deliverable. It coordinates screenplay development, cinematographic planning, sound design, and musical scoring to produce a professional film project.

**What this accomplishes:**
- Feature-quality screenplay with three-act structure, character arcs, and cinematic visual storytelling
- Comprehensive cinematographic treatment including shot lists, lighting plots, and visual style guide
- Complete sound design package with SFX, foley, ambience, and spatial audio
- Original musical score synchronized to picture with thematic development

**When to use:**
- Short film projects (5-30 minutes)
- Feature film development (90-120 minutes)
- Film festival submissions
- Narrative video content requiring professional production values

**Expected outcomes:**
- Production-ready screenplay
- Shot-by-shot cinematographic plan
- Complete audio post-production package
- Integrated audio-visual deliverable

**Estimated execution time:** 4-8 weeks for complete workflow (depending on film length)

## Multi-Agent Orchestration Strategy

### **Phase 1: Screenplay Development**
Deploy `screenwriter` to:
- Develop feature-length or short film screenplay from concept or treatment
- Create three-act structure with proper turning points, character arcs, and dramatic pacing
- Write cinematic dialogue with subtext, character voice distinction, and economy
- Format to industry standards (Final Draft/Fade In), proper scene headings and action lines
- Deliver table-read-tested script with coverage feedback incorporated

**Why this agent:** Screenwriter specializes in feature film narrative structure, visual storytelling, and industry-standard screenplay formatting. Distinct from tv-writer (episodic) and comedy-writer (stand-up).

### **Phase 2: Visual Treatment**
Engage `cinematographer` to:
- Analyze screenplay for key visual moments, emotional beats, and cinematic opportunities
- Create comprehensive shot list with camera angles, movement, lens choices, and framing
- Design lighting plots for each scene matching mood, genre conventions, and practical constraints
- Develop color palette and look book with reference images, LUT choices, and visual style guide
- Plan coverage strategy ensuring adequate editorial options while maintaining directorial vision

**Why this agent:** Cinematographer translates written scenes into visual language through camera work, lighting design, and shot composition. Works collaboratively with screenwriter to enhance visual storytelling.

**Handoff:** Screenplay provides scene breakdowns, emotional arcs, and key moments. Cinematographer identifies visual opportunities and technical requirements.

### **Phase 3: Sound Design**
Use `sound-designer` to:
- Create custom sound effects library tailored to film's specific needs
- Design soundscapes and ambiences for each location and scene
- Perform or source foley for all physical actions (footsteps, cloth, props, body mechanics)
- Implement spatial audio with proper stereo imaging, reverb, and 5.1/7.1 surround placement
- Deliver layered sound effects stems (hard FX, backgrounds, foley, designed elements) for final mix

**Why this agent:** Sound-designer specializes in creating immersive audio environments through SFX creation, foley performance, and spatial audio implementation. Distinct from audio-engineer (technical mixing) and music-composer (musical content).

**Handoff:** Screenplay and cinematographic treatment identify sound needs, emotional tone, and sync points. Sound-designer creates sonic world supporting visual narrative.

### **Phase 4: Musical Scoring**
Deploy `music-composer` to:
- Analyze film structure to identify spotting points (where music enters/exits)
- Develop main themes and leitmotifs for characters, relationships, and emotional arcs
- Compose scene-specific underscores matching visual pacing and emotional beats
- Create orchestral mockups or live recordings synchronized to picture
- Deliver music stems (strings, woodwinds, brass, percussion, synths) for final mix flexibility

**Why this agent:** Music-composer creates original scores with thematic development, orchestration, and emotional storytelling through music. Coordinates with sound-designer for audio balance.

**Handoff:** Locked picture with temp music provides timing references. Composer replaces temp with original score matching visual rhythm and emotional intent.

### **Phase 5: Integration & Final Mix**
Coordinate `project-orchestrator` to:
- Assemble all audio and visual elements into cohesive deliverable
- Ensure proper sync between picture, dialogue, sound effects, foley, and music
- Balance all audio stems for optimal listening experience (dialogue intelligibility prioritized)
- Export final deliverables in required formats (DCP for theatrical, ProRes for festivals, H.264 for streaming)
- Prepare submission materials (press kits, stills, synopsis, director's statement)

**Why this agent:** Project-orchestrator manages cross-department integration, ensures no creative silos, and delivers complete functional system meeting all delivery specs.

## Execution Flow

```
Phase 1: Screenplay Development (screenwriter)
    ↓ [Script locked, table read complete]
Phase 2: Visual Treatment (cinematographer)
    ↓ [Shot list, lighting plots, look book delivered]
Phase 3a: Sound Design (sound-designer)  ┐
                                         ├→ Audio Integration
Phase 3b: Musical Scoring (music-composer) ┘
    ↓ [All audio stems delivered]
Phase 4: Final Integration (project-orchestrator)
    ↓
[Complete film deliverable with all audio-visual elements]
```

## Expected Deliverables

- **Screenplay**: Production-ready script (PDF format, 90-120 pages for feature or 5-30 pages for short)
- **Shot List**: Comprehensive scene-by-scene breakdown with camera angles, lenses, movement (Excel/Google Sheets)
- **Lighting Plots**: Scene lighting diagrams with instrument types, positions, color temps (PDF diagrams)
- **Look Book**: Visual reference document with color palette, mood boards, cinematographic style (PDF)
- **Sound Effects**: Organized SFX library with naming convention, WAV 48kHz 24-bit (folder structure)
- **Foley Tracks**: Synchronized foley performances for footsteps, cloth, props (multi-track WAV)
- **Ambience/BG**: Location-specific atmospheres and backgrounds (stereo/5.1 WAV)
- **Music Score**: Full orchestral score synchronized to picture with stems (WAV stems + stereo mix)
- **Final Mix**: Dialogue, music, effects stems plus stereo/5.1 final mix (-23 LUFS for broadcast)
- **Deliverables Package**: DCP, ProRes, H.264 exports plus festival submission materials

## Success Criteria

- [ ] Screenplay passes professional script coverage with "Recommend" or "Consider" rating
- [ ] Shot list covers 100% of script scenes with adequate coverage for editing
- [ ] Lighting plots are practical and achievable within budget constraints
- [ ] Sound design enhances emotional impact without overwhelming dialogue
- [ ] Musical score supports narrative without overwhelming visual storytelling
- [ ] All audio properly synchronized to picture with frame-accurate sync
- [ ] Final mix meets broadcast loudness standards (-23 LUFS for EBU R128)
- [ ] Deliverable formats meet festival/distribution technical requirements
- [ ] All creative elements integrate cohesively supporting unified artistic vision

## Common Issues and Solutions

**Issue:** Screenplay too long (over 120 pages)
**Solution:** Screenwriter revises for economy, cuts subplots, tightens dialogue
**Prevention:** Set page count target early, outline before writing full draft

**Issue:** Shot list requires equipment beyond budget
**Solution:** Cinematographer adapts plan for available gear, creative workarounds for ambitious shots
**Prevention:** Budget/equipment discussion before shot planning begins

**Issue:** Sound effects don't match picture (sync drift)
**Solution:** Sound-designer re-syncs to locked picture, checks frame rate match
**Prevention:** Work from locked picture cut, verify timecode consistency

**Issue:** Music overwrites dialogue or sound effects in key moments
**Solution:** Composer adjusts orchestration, leaves frequency space for dialogue
**Prevention:** Spotting session identifies dialogue-heavy scenes, composer plans sparse arrangements

**Issue:** Final deliverable doesn't meet festival technical specs
**Solution:** Re-export with correct codec, resolution, frame rate, loudness standards
**Prevention:** Research festival specs before final delivery, validate early test exports

## Related Commands

- **`/development:screenplay-writing`**: Focus solely on screenplay development without production planning
- **`/creative:music-composition`**: Standalone music composition without film sync
- **`/quality:production-readiness`**: Comprehensive pre-delivery QA for film festivals and distribution

## Notes

**Production Stages:**
- Pre-production: Phases 1-2 (screenplay and cinematographic planning)
- Production: Filming based on Phase 2 deliverables (not orchestrated by this command)
- Post-production: Phases 3-5 (sound design, music, final integration)

**Budget Considerations:**
- Low-budget indie: Prioritize sound design and music over expensive camera equipment
- High-budget: All phases can be maximally ambitious with full crew and orchestra

**Genre-Specific Adaptations:**
- **Horror**: Heavy emphasis on sound design (sound-designer leads), sparse music, cinematographer focuses on lighting contrast
- **Action**: Cinematographer focuses on dynamic camera movement, sound-designer emphasizes impacts and intensity
- **Drama**: Screenwriter and cinematographer lead, music supports emotional beats subtly
- **Documentary**: Adapt workflow to observational style, naturalistic sound, minimal score

**Collaboration Points:**
- Cinematographer and screenwriter: Visual script analysis identifies cinematic moments
- Sound-designer and music-composer: Sonic territory negotiation (who handles which frequency ranges, emotional spaces)
- All agents and project-orchestrator: Regular check-ins ensure unified artistic vision

**Timeline Estimates:**
- Short film (5-15 min): 2-4 weeks
- Medium short (15-30 min): 4-6 weeks
- Feature film (90-120 min): 8-12 weeks

This workflow ensures professional-quality film production through coordinated specialist expertise from script to final deliverable.
