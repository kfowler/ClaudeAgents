---
name: album-production
description: Complete music album production workflow coordinating music-composer, poet (lyricist), sound-designer, and audio-engineer for professional album release
---

# Album Production

## Overview

This command orchestrates a complete music album production from composition to mastered release. It coordinates original composition, lyric writing, sound design, and audio engineering to produce a professional music album ready for streaming, physical release, or sync licensing.

**What this accomplishes:**
- Original musical compositions with thematic cohesion across album
- Professional lyrics with poetic depth, musicality, and storytelling
- Sound design elements (interludes, transitions, textural layers)
- Mix and master to streaming loudness standards (-14 LUFS, genre-appropriate)

**When to use:**
- Indie music releases (EP, LP, concept album)
- Film/game soundtrack albums
- Singer-songwriter projects
- Instrumental or vocal music production

**Expected outcomes:**
- 8-14 professionally composed and produced tracks
- Cohesive album with narrative or thematic arc
- Distribution-ready masters (WAV + MP3/AAC)

**Estimated execution time:** 3-6 months for full LP

## Multi-Agent Orchestration Strategy

### **Phase 1: Composition & Arrangement**
Deploy `music-composer` to:
- Compose 8-14 original songs/pieces with thematic and musical coherence
- Develop main themes, harmonic progressions, and melodic motifs recurring across album
- Arrange for target instrumentation (band, orchestral, electronic, hybrid)
- Create production demos (MIDI mockups or rough recordings)
- Establish album arc (song order, key relationships, tempo pacing, emotional journey)

**Why this agent:** Music-composer specializes in original composition, thematic development, orchestration, and music theory application.

### **Phase 2: Lyric Writing** (for vocal music)
Engage `poet` to:
- Write lyrics matching melodic rhythm, phrasing, and emotional tone of compositions
- Develop album narrative or thematic through-line connecting songs
- Apply poetic devices (metaphor, imagery, sound devices) for memorable, singable lyrics
- Ensure lyrics fit vocal range and prosody (stressed syllables on strong beats)
- Deliver lyrics with performance notes (phrasing, emphasis, emotional delivery)

**Why this agent:** Poet brings literary craft to lyric writing with attention to rhythm, imagery, and emotional depth. Works collaboratively with music-composer on melody-lyric integration.

**Handoff:** Composer provides melodic structure, tempo, key, and emotional intent. Poet crafts lyrics fitting musical phrasing and enhancing thematic content.

### **Phase 3: Production & Sound Design**
Use `sound-designer` to:
- Design album interludes, transitions, and textural sound beds
- Create signature sonic elements (risers, impacts, glitchy textures, field recordings)
- Layer ambient soundscapes under songs for atmosphere (nature sounds, urban environments, analog noise)
- Design album opening and closing sonic bookends for cohesion
- Deliver production-ready sound design stems integrated with music

**Why this agent:** Sound-designer adds sonic depth beyond traditional instrumentation, creating immersive album experience with textural layers and transitional elements.

**Handoff:** Music compositions define harmonic and rhythmic framework. Sound-designer adds non-musical sonic elements enhancing atmosphere without competing with music.

### **Phase 4: Mixing & Mastering**
Coordinate `audio-engineer` to:
- Mix individual tracks balancing instruments, vocals, effects for clarity and impact
- Apply EQ, compression, reverb, and creative effects achieving cohesive sonic signature
- Master album for loudness consistency (-14 LUFS for streaming), frequency balance, and dynamic range
- Create album versions (explicit/clean, instrumental, stems for remixing/licensing)
- Deliver distribution formats (WAV masters, MP3/AAC 320kbps, metadata embedded)

**Why this agent:** Audio-engineer provides technical expertise in mixing, mastering, and final audio delivery meeting industry standards.

**Handoff:** Music, lyrics, and sound design provide creative content. Audio-engineer optimizes sonic quality and prepares for distribution.

## Execution Flow

```
Phase 1: Composition & Arrangement (music-composer)
    ↓ [8-14 songs composed, album arc defined]
Phase 2: Lyric Writing (poet) [for vocal music]
    ↓ [Lyrics written, phrasing finalized]
Phase 3: Production & Sound Design (sound-designer)
    ↓ [Interludes, textures, transitions added]
Phase 4: Mixing & Mastering (audio-engineer)
    ↓
[Distribution-ready album masters with metadata]
```

## Expected Deliverables

- **Album Compositions**: 8-14 original songs with sheet music and production demos (PDF scores, MIDI files, rough mixes)
- **Lyrics**: Complete lyric sheets with phrasing, rhyme schemes, thematic notes (PDF/Google Docs)
- **Sound Design Assets**: Interludes, transitions, textural layers (WAV stems, organized folders)
- **Mixed Tracks**: Individual song mixes with proper gain staging, effects, and balance (WAV 24-bit/48kHz)
- **Mastered Album**: Final masters with loudness optimization, sequencing, fades (WAV 24-bit/48kHz + 16-bit/44.1kHz)
- **Distribution Formats**: MP3 320kbps, AAC 256kbps with ID3 tags, album art embedded
- **Stem Mixes**: Instrumental stems (drums, bass, guitars, keys, vocals) for sync licensing or remixing
- **Metadata Package**: Track titles, ISRC codes, credits, lyrics, album art (3000x3000px minimum)

## Success Criteria

- [ ] Album has thematic coherence with consistent sonic signature across tracks
- [ ] Lyrics are memorable, singable, and enhance emotional impact of music
- [ ] Sound design elements add atmosphere without overwhelming musical content
- [ ] Mixes are balanced with clear vocal intelligibility and impactful instrumentation
- [ ] Masters meet streaming loudness targets (-14 LUFS ±1dB) with appropriate dynamic range
- [ ] Album pacing creates satisfying listening journey from opening to closing track
- [ ] Distribution files meet platform specs (Spotify, Apple Music, Bandcamp)
- [ ] All tracks free of technical issues (clipping, phase problems, unwanted artifacts)

## Common Issues and Solutions

**Issue:** Lyrics don't fit melodic phrasing (too many syllables or awkward stresses)
**Solution:** Poet and composer collaborate on melodic adjustments or lyric rewrites
**Prevention:** Composer provides detailed melody with syllable counts, poet writes to spec

**Issue:** Sound design elements clash with harmonic content of songs
**Solution:** Sound-designer filters out conflicting frequencies, uses atonal/noise-based elements
**Prevention:** Sound-designer receives key and harmonic information, avoids tonal clashes

**Issue:** Album lacks cohesion, sounds like random song collection
**Solution:** Composer establishes musical motifs recurring across tracks, sound-designer creates transitional interludes
**Prevention:** Define album concept and arc before composition, intentional thematic planning

**Issue:** Mix sounds muddy with too many competing elements
**Solution:** Audio-engineer applies subtractive EQ, removes unnecessary frequencies, creates space
**Prevention:** Arrange with frequency balance in mind, avoid overcrowding mid-range

**Issue:** Masters too loud (over-compressed) or too quiet (under-competitive)
**Solution:** Audio-engineer adjusts mastering chain, finds sweet spot for genre and platform
**Prevention:** Reference commercial releases in genre, target appropriate loudness and dynamics

## Related Commands

- **`/creative:music-composition`**: Standalone composition without full production pipeline
- **`/creative:poetry-collection`**: Poetry writing without musical integration
- **`/quality:audio-mastering`**: Focus on mastering without composition or production phases

## Notes

**Genre-Specific Workflows:**
- **Singer-Songwriter**: Heavy poet involvement, intimate production, minimal sound design
- **Electronic/Ambient**: Music-composer and sound-designer collaborate closely, possibly no lyrics
- **Rock/Indie Band**: Composer writes for band instrumentation, collaborative arrangement process
- **Hip-Hop**: Poet writes rap lyrics with internal rhyme and flow, composer produces beats
- **Orchestral/Instrumental**: No lyric phase, focus on composition depth and orchestration

**Distribution Platforms:**
- **Streaming (Spotify, Apple Music, Tidal)**: Use aggregators (DistroKid, CD Baby, TuneCore)
- **Bandcamp**: Artist-friendly, higher revenue share, direct fan support
- **Physical (Vinyl, CD, Cassette)**: Requires manufacturing, higher upfront cost, collector appeal
- **Sync Licensing (TV/Film/Games)**: Instrumental versions critical, metadata and licensing clear

**Monetization:**
- **Streaming Revenue**: Low per-stream payouts, requires high volume
- **Physical Sales**: Higher margins, limited audience, niche appeal
- **Sync Licensing**: High-value placements, requires instrumental/stem versions
- **Live Performance**: Album supports touring revenue, merch sales
- **Patreon/Crowdfunding**: Direct fan support, behind-the-scenes content

**Timeline Estimates:**
- **EP (4-6 tracks)**: 2-3 months
- **LP (10-14 tracks)**: 4-6 months
- **Concept Album**: 6-12 months (more complex thematic development)

**Collaboration Models:**
- **Solo Artist**: All creative decisions by one person, specialists execute vision
- **Band**: Democratic or songwriter-led, specialists support collective vision
- **Producer-Driven**: Producer (music-composer + audio-engineer hybrid) leads creative direction

This workflow ensures professional album production through coordinated specialist expertise from composition to distribution-ready masters.
