# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/ngadukun/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/ngadukun/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that renders a newspaper-style front page summing up Thursday 26 November 2026's world news in a single image: Trump's sweeping new tariffs on 14 nations, the Houthi drone strike on Riyadh's PIF Tower, Nvidia's downgrade watch after the Huang turmoil, the first Pakistani astronaut bound for China's space station, BepiColombo's arrival in Mercury orbit, and the day's markets — drawn as one 724x1024 front page.

## Run it

```sh
python3 main.py
```

The program writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` when set, otherwise next to the script. It runs on a stdlib-only Python 3.13: Pillow is vendored as a wheel in `vendor/` and unpacked at run time, so no packages need installing.

---

<sub>Entered on [make.fun](https://make.fun/?ref=76a09jb0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
