---
name: dance-performance
description: Complete dance performance production workflow coordinating choreographer, music-composer, cinematographer, and sound-designer for live or filmed dance work
---

# Dance Performance

## Overview

This command orchestrates a complete dance performance production from choreographic concept to stage-ready or filmed performance. It coordinates movement design, musical composition, visual documentation, and sound design to produce a professional dance work for theater, film, or multimedia presentation.

**What this accomplishes:**
- Original choreography with thematic development and spatial design
- Custom musical score synchronized to movement and emotional arc
- Professional documentation (multi-angle video, lighting design) for archival or distribution
- Sound design elements enhancing live or recorded performance

**When to use:**
- Contemporary dance concerts or showcases
- Dance film/video projects
- Musical theater choreography with original music
- Site-specific or multimedia dance installations

**Expected outcomes:**
- Performance-ready choreography with notation and teaching materials
- Original score matching dance structure and emotional beats
- Professional video documentation or live performance technical plan

**Estimated execution time:** 2-4 months for 10-20 minute dance work

## Multi-Agent Orchestration Strategy

### **Phase 1: Choreographic Development**
Deploy `choreographer` to:
- Create movement vocabulary and phrase material aligned with concept or theme
- Develop spatial design with formations, pathways, and level changes
- Structure choreography to musical form (if pre-existing music) or abstract structure (if original music)
- Rehearse with dancers refining technique, timing, and performance quality
- Document choreography through video (multi-angle), notation (Labanotation), and count sheets

**Why this agent:** Choreographer specializes in movement composition, spatial design, and physical storytelling across dance styles (ballet, contemporary, hip-hop, etc.).

### **Phase 2: Musical Composition** (for original music)
Engage `music-composer` to:
- Analyze choreographic structure identifying key moments, transitions, and climaxes
- Compose music matching dance phrasing, tempo, and emotional arc
- Coordinate with choreographer on counts, accents, and musical signposts
- Create rehearsal recordings (piano reduction or MIDI) and final production score
- Deliver performance-ready music (live musicians or playback track)

**Why this agent:** Music-composer creates original scores synchronized to dance, understanding how music supports movement without overwhelming.

**Handoff:** Choreographer provides movement structure with counts, tempo, and emotional beats. Composer creates music fitting dance architecture while maintaining musical integrity.

**Note:** If using pre-existing music, this phase focuses on music editing, licensing, and synchronization instead of composition.

### **Phase 3: Performance Documentation or Filming**
Use `cinematographer` to:
- Design lighting plot for stage performance (color, intensity, focus, cues)
- Plan camera angles for dance film (wide for full body, medium for formations, close for detail)
- Coordinate with choreographer on optimal angles showing movement clearly
- Execute filming (multi-camera setup) or lighting design (stage performance)
- Deliver professional video documentation or technical lighting plan with cue sheet

**Why this agent:** Cinematographer understands visual storytelling through camera and lighting, essential for both live performance design and dance film production.

**Handoff:** Choreography locked, music finalized. Cinematographer enhances visual presentation through lighting (live) or camera work (film).

### **Phase 4: Sound Design & Audio Post** (for filmed work or immersive live performance)
Deploy `sound-designer` to:
- Design spatial audio for immersive live performance (if applicable)
- Edit and mix audio for dance film (balance music with environmental sounds if needed)
- Add sound effects or ambient textures enhancing thematic elements (not typical for pure dance, but relevant for multimedia)
- Deliver final audio mix synchronized to video or live performance cue sheet

**Why this agent:** Sound-designer handles technical audio production, spatial audio, and mixing for optimal listening experience.

**Handoff:** Music and any sound design elements integrated with choreography. Sound-designer optimizes final audio delivery.

## Execution Flow

### For Live Performance:
```
Phase 1: Choreographic Development (choreographer)
    ↓ [Choreography complete, dancers rehearsed]
Phase 2: Musical Composition (music-composer) [if original music]
    ↓ [Score composed, rehearsal recordings delivered]
Phase 3: Lighting Design (cinematographer)
    ↓ [Lighting plot with cues]
Phase 4: Technical Rehearsal & Performance
    ↓
[Live performance ready with all technical elements]
```

### For Dance Film:
```
Phase 1: Choreographic Development (choreographer)
    ↓ [Choreography complete, dancers rehearsed]
Phase 2: Musical Composition (music-composer) [if original music]
    ↓ [Score composed, playback track ready]
Phase 3: Filming (cinematographer)
    ↓ [Multi-angle footage captured]
Phase 4: Audio/Video Post-Production (sound-designer + video editor)
    ↓
[Finished dance film ready for distribution]
```

## Expected Deliverables

### For Live Performance:
- **Choreography Documentation**: Video rehearsal (multi-angle), notation, count sheets (PDF + video files)
- **Musical Score**: Sheet music for live musicians or playback track with timecode (PDF score, WAV/MP3 playback)
- **Lighting Plot**: Stage diagram with instrument positions, color gels, focus points, cue sheet (PDF diagram + spreadsheet)
- **Performance Materials**: Program notes, choreographer's statement, dancer bios (PDF)
- **Archival Video**: Single-camera or multi-camera recording of live performance (HD video)

### For Dance Film:
- **Choreography Documentation**: Same as live performance
- **Musical Score**: Final mixed audio track synchronized to picture
- **Dance Film**: Edited video with color correction, titles, credits (MP4/MOV, 1080p or 4K)
- **Behind-the-Scenes**: Optional rehearsal footage, interviews, making-of content (video)
- **Distribution Formats**: Festival submission (DCP, ProRes), online (H.264, compressed), social media (vertical formats)

## Success Criteria

- [ ] Choreography is technically polished with dancers performing at high level
- [ ] Music (original or edited) supports movement without overwhelming dance
- [ ] Lighting design enhances visibility and mood without distracting from movement
- [ ] Documentation clearly shows choreographic spatial design and dancer technique
- [ ] Audio mix is balanced with music clearly audible but not overpowering
- [ ] For live performance: All technical cues (lights, sound) are rehearsed and reliable
- [ ] For dance film: Editing rhythm matches choreographic phrasing
- [ ] Final product represents choreographer's artistic vision faithfully

## Common Issues and Solutions

**Issue:** Music doesn't match choreographic counts or phrasing
**Solution:** Composer adjusts tempo or structure, choreographer adapts movement timing
**Prevention:** Detailed spotting session early, share counts and video of movement before composing

**Issue:** Lighting too bright or too dark, dancers not visible
**Solution:** Cinematographer adjusts intensity and focus during technical rehearsal
**Prevention:** Lighting designer attends dress rehearsal, collaborates with choreographer on levels

**Issue:** Camera angles don't capture spatial relationships or key movements
**Solution:** Reshoot with adjusted camera positions, wider lenses, or different heights
**Prevention:** Cinematographer reviews rehearsal video, identifies optimal angles before shoot

**Issue:** Audio mix buries music under environmental noise or vice versa
**Solution:** Sound-designer rebalances mix, applies EQ to separate elements
**Prevention:** Record clean audio in controlled environment, avoid competing sound sources

**Issue:** Dancers not performance-ready by technical rehearsal
**Solution:** Add rehearsals, simplify choreography, or postpone performance
**Prevention:** Realistic rehearsal timeline (minimum 6-8 weeks for 10-minute piece)

**Issue:** Dance film editing rhythm doesn't match movement
**Solution:** Video editor cuts on movement accents, respects choreographic phrasing
**Prevention:** Editor consults with choreographer, understands dance structure before editing

## Related Commands

- **`/creative:music-composition`**: Standalone music composition for existing choreography
- **`/creative:film-production`**: Full cinematic production if dance film requires narrative elements
- **`/creative:live-performance-production`**: Broader live performance coordination including non-dance elements

## Notes

**Dance Styles & Production Needs:**
- **Ballet**: Classical staging, traditional lighting, orchestral music typical
- **Contemporary**: Flexible staging, experimental lighting, original scores common
- **Hip-Hop**: Urban aesthetics, electronic/hip-hop music, dynamic camera work for film
- **Musical Theater**: Integrated with narrative, elaborate costumes and sets, Broadway-style lighting

**Performance Venues:**
- **Proscenium Theater**: Traditional frontal view, deep stage, flies for lighting
- **Black Box**: Flexible configuration, intimate, adaptable lighting grid
- **Site-Specific**: Non-traditional spaces (galleries, outdoor, urban), lighting challenges
- **Film/Video**: Complete control over angles, lighting, editing, but no live energy

**Music Options:**
- **Original Composition**: Custom-fit to choreography, highest artistic control, costly
- **Pre-Existing Music**: Licensing required for public performance or commercial film, less expensive
- **Silence or Environmental Sound**: Valid artistic choice, emphasizes pure movement
- **Collaboration**: Composer and choreographer create work simultaneously, organic integration

**Budget Considerations:**
- **Low Budget**: Use pre-existing music (license if public), minimal lighting, smartphone documentation
- **Mid Budget**: Commission short original score, rent professional lighting, hire videographer
- **High Budget**: Full orchestral commission, elaborate lighting design, multi-camera film crew

**Timeline Estimates:**
- **Short Solo (3-5 min)**: 3-6 weeks choreography + 2 weeks production
- **Group Piece (10-15 min)**: 8-12 weeks choreography + 3-4 weeks production
- **Evening-Length (45-60 min)**: 4-6 months choreography + 6-8 weeks production

**Distribution & Presentation:**
- **Live Performance**: Theater rental, ticketing, promotion, limited reach but immediate audience connection
- **Dance Film**: Festivals (American Dance Film Festival, Dance Camera West), online platforms (Vimeo, YouTube), broader reach
- **Hybrid**: Live performance with professional filming for later distribution
- **Archival**: Documentation for grants, archives, future remounting (not public distribution)

**Collaboration Dynamics:**
- Choreographer leads artistic vision
- Composer provides musical support enhancing movement
- Cinematographer (lighting designer or DP) enhances visual presentation
- Sound-designer ensures technical audio excellence
- All specialists respect dance as primary art form

This workflow ensures professional dance performance production through coordinated specialist expertise from choreography to performance or film completion.
