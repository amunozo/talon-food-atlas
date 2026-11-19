# Fan transcription of the Grains Ranked final board (dp_1u2KJx-0)

Method: yt-dlp pulled the info JSON and all 2171 comments on 2026-11-19. Comment text and metadata below come from that pull. Source video: [Grains Ranked](https://www.youtube.com/watch?v=dp_1u2KJx-0).

## Does the description link a fan transcription, and is there a comment transcribing the whole final board?

### Takeaway
The description links nothing of the kind. One root comment, by @zero_zero2771, transcribes the whole board. It has 0 likes, is not pinned, and was posted in June 2026, roughly 3.5 years after the video. It is thin evidence for the CSV's "fan transcription" note.

### Cited Findings
- The description has only the blurb, a "What I Would Change" note (Talon says he left the C tier empty), a USDA data note, and chapter timestamps (Teff 13:57, Triticale 14:30, Wheat 14:53, Wild Rice 16:39). It has no fan link, spreadsheet or comment link. — [video](https://www.youtube.com/watch?v=dp_1u2KJx-0)
- Only 1 of the 2171 comments is a full board transcription: author @zero_zero2771, comment id UgxB0QKOXqVONfE8UUh4AaABAg, link `https://www.youtube.com/watch?v=dp_1u2KJx-0&lc=UgxB0QKOXqVONfE8UUh4AaABAg`. It has 0 likes. It is not pinned. The timestamp is 2026-06-19, day-rounded as yt-dlp gives it. — [comment](https://www.youtube.com/watch?v=dp_1u2KJx-0&lc=UgxB0QKOXqVONfE8UUh4AaABAg)
- Its text reads:
  - Top tier: Amaranth, Buckwheat, Corn, Einkorn, Oats, Rye, Wheat
  - A tier: Barley, Bulgur, Freekeh, Khorasan, Quinoa, Spelt, Teff, Triticale
  - B tier: Farro, Fonio, Millet, Brown Rice, Sorghum, Wild Rice
  - C tier: (empty)
  - D tier: White Rice
- The only pinned comment is by @Talon_Fitness (569 likes), asking viewers to watch through the conclusion. It has no board. — [comment](https://www.youtube.com/watch?v=dp_1u2KJx-0&lc=UgzBgG7Ls-xh9MIQuKZ4AaABAg)
- Other comments confirm parts of the board only indirectly: @comptegoogle511 ("Wild rice in B and wheat in A+????") and @sebastianorlowski2176 (wheat above quinoa and wild rice). — [comment](https://www.youtube.com/watch?v=dp_1u2KJx-0&lc=UgxB0QKOXqVONfE8UUh4AaABAg)

### Inferences
- The comment's empty C tier matches the description's statement that Talon left C unused. That supports the transcription being accurate.
- The CSV note "cross-checked against the fan transcription" most plausibly refers to this comment, but nothing proves it. The comment's age and 0 likes make it a weak, single-source cross-check.

### Gaps
- yt-dlp date is day-rounded and I did not verify it in the UI. The comment id has no author-history info beyond the handle.

## Do the four late grains agree with the CSV?

### Takeaway
Yes, all four agree, and the whole board matches too (23 grains).

### Cited Findings
- The comment gives Teff A, Triticale A, Wheat top tier (star), Wild Rice B. The CSV rows in `/home/alberto/projects/personal/data/talon-food-atlas/talon-food-atlas-rankings.csv` (grep "Grains Ranked") say Teff A (837s), Triticale A (870s), Wheat star (893s), Wild Rice B (999s). — [comment](https://www.youtube.com/watch?v=dp_1u2KJx-0&lc=UgxB0QKOXqVONfE8UUh4AaABAg)
- The other 19 grains also match the CSV tier for tier. Star: Amaranth, Buckwheat, Corn, Einkorn, Oats, Rye. A: Barley, Bulgur, Freekeh, Khorasan, Quinoa, Spelt. B: Farro, Fonio, Millet, Brown Rice, Sorghum. D: White Rice. — [CSV compare, local file]
- Oddity in the CSV, not the comment: the Teff, Triticale, Wheat and Wild Rice rows have chapter_url / second URL columns pointing at &t=870s for every grain, and the Wheat row's last URL is &t=970s while Wild Rice is 999s. These look like template columns. Not investigated further.

### Inferences
- The comment is independent only in the weak sense that it was written by a viewer. Its author may have taken the placements from the video, not from other data. Agreement therefore confirms the CSV against a second viewer's reading, not against a ground truth such as a frame capture.

### Gaps
- I did not look at video frames, so the board itself is unverified by me.

## Is a recurring fan transcriber visible on other episodes?

### Takeaway
No evidence of one in the sample checked. @zero_zero2771 has no other comments in the four episodes sampled.

### Cited Findings
- I scanned comments of Beans (0ekX1bE_gIM, 2455 comments), Flours (vIZQ8YCwzL0, 380), Cereals (kYmlw01oqPQ, 1095) and Nuts (K8HuhaKObZs, 2853) for multi-line "X tier:" lists and for author @zero_zero2771. Result: no board transcription and no comments by that author. The only tier-list-like comment was an unrelated sweeteners ranking by @BALTOBOULBOBBI on the Nuts video. — [Nuts video](https://www.youtube.com/watch?v=K8HuhaKObZs)

### Inferences
- Board transcriptions in comments appear rare. The Grains one looks like a one-off.

### Gaps
- Only 4 of about 30 episodes sampled, and a regex search, so a differently formatted transcription could be missed. Raw JSON is in the scratchpad `yt/` directory, which may be cleared.
