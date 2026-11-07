TL;DR
Build a small, complete game and a model-driven agent that plays it, then compare that player with a cheap baseline . You may reconstruct a classic, make an original game from scratch, or adapt an existing codebase.

Choose a game and a finishable scope : a complete loop and a clear ending or bounded episode .
Direct your building agent team : implementation, a reusable skill , and independent review , with evidence .
Provide the five-operation game interface : enforce legal actions , information boundaries , and episode limits.
Compare a model-driven player with a cheap baseline : declare the suite before tuning; report repeated live trials and failures.
Run deterministic CI and a human playtest : check rules and regressions, and have at least one person, anyone, play your build while you watch.
Write the peer review after submission : silent-playtester notes on three assigned classmates' recordings, assigned November 9 and due before class November 16.
Submit your course-repository PR URL on CourseWorks by November 7, 11:59 p.m. Put your work in game-dev-f26/midterms/<github-login>/ ; include the README, evaluation, agent-team log, playtest notes, and recording link. Check the rubric before submitting.
What you are building
A bounded, complete, playable game, built by an agent team under your direction, plus a separate agent that plays it through an explicit observation/action interface , compared against a cheap baseline on a small suite you declare before tuning. Keep the complete submission in your folder in the course repository, with one PR and one recording.

Choose your game
Choose either a classic reconstruction or an original game . Both are eligible for full credit. You may implement your own game completely from scratch. Choose your design and your implementation starting point separately.

Design and starting point
Reconstruct a classic. Reproduce a bounded portion of an existing game's rules and experience. Explain omissions and adaptations. Your Week 3 choice is a useful starting point; other genres are welcome.
Design an original game. Specify your own rules, decisions, and intended player experience. Ground design choices in references, observations, and playtests where useful. Originality does not require inventing every mechanic or writing an engine from scratch.
For either design, you may build from scratch or adapt an existing codebase whose terms permit reuse. Starting from scratch is a valid choice even when reusable code exists. When adapting code, make inherited work and your contributions inspectable through a fork and commits or a patch set. Credit all sources and document their terms. The same interface, agent , evaluation, and evidence requirements apply to both starting points.

The Get Out! variation and the Motivation Atlas minigame are practice and inspiration. Carry forward what you learned there about rules, scope, and agent configuration , and submit a game built for this brief that meets all of its requirements.

Infocom offers useful reconstruction examples: Zork I, Planetfall, Wishbringer, Enchanter, and Mini-Zork. Board, puzzle, arcade, and turn-based strategy games are equally welcome. A small original deduction puzzle, one arena encounter, or a short strategy scenario can also work well.

Rules and evidence
Keep a rule/source map for either design. For inherited rules, retain the Week 2 Recap's labels: code , manual , observed , or assumed , with locators to the evidence. Label your own rules and deliberate adaptations design , pointing to your rule specification and explaining the choice. Use assumed for an unverified inference about a source game, and design for a rule you intentionally chose. Your specification should make initial state, valid actions, transitions, scoring, and termination inspectable. Cite reference games and reused material even when your rules are original.

A complete small game
Bound the scope with the same criteria for every genre: a complete core loop , meaningful player decisions, authoritative state and legal actions , a clear ending or bounded episode , and a feasible agent evaluation. A small game can earn full credit. Its completed experience and the quality of the experiment matter more than the size of the proposed future game.

An adventure might have a few rooms and connected puzzles; a board game might use its complete rules; an arcade game might use one level with a fixed-step simulation. Room counts and NPCs are not universal requirements. For very small games such as tic-tac-toe, put the depth in verified rules, strong baselines , and the quality of the experiment. Full-game ports, graphics, and sound are optional. If your reference or original concept is large, choose one bounded episode and state its boundaries.

Relation to the final project
Deliver a complete small midterm game that can be played and evaluated on its own. Details of final-project ideation, team formation, and any reuse of midterm concepts or code will be announced separately.

Language and engine choice require no special permission. The supplied Python/Pyxel starter is one example; the Atlas TypeScript template is another. Document setup, play, and evaluation commands for your own stack. Game quality, design judgment and evidence are assessed across platforms; no particular engine is taught.

Three responsibilities
Component	Access and responsibility	Evidence
Building agent team	implementation agent , reusable skill and independent review task; scoped repository access	configuration files, reviewed PRs or review transcripts, and a one-page agent team log
Game-playing agent	observations, allowed actions and bounded episode history; no repository tools, answer key or hidden state	executable player, action trace and baseline comparison
Game engine and evaluator	code validates moves and computes rule-based outcomes ; humans assess experience and ambiguous judgments	tests, episode results and human playtest notes
You direct the agent team and own the result. Practice game-project roles through agents that examine design, production, technical, art and quality questions. Keep their recommendations and your decisions inspectable. An in-game narrator or NPC can enrich the design, but it does not satisfy the player-agent requirement unless it actually selects and submits game actions.

What counts as agent-team evidence
The course is model-agnostic and coding-assistant-agnostic. Each of the three roles needs an executable or inspectable artifact in the repository; any of these forms satisfies it.

Role	Claude Code	Codex	Other assistants
Implementation agent	CLAUDE.md and the session that built the feature, linked from the PR	AGENTS.md and the Codex session or cloud task, linked from the PR	the assistant's project instructions file and a linked session
Reusable skill	a skill under .claude/skills/	a skill or prompt file under .codex/ or skills/ , invoked by name in at least two sessions	a saved prompt or custom instruction, committed and invoked twice
Independent review	a rules-reviewer style subagent, or a review session that only reads	a separate Codex review session (cloud code review, or a fresh CLI session with read-only instructions), its findings committed as review.md or PR comments	a second assistant or session with read-only instructions, findings committed
"Independent" means the reviewer did not write the code it reviews and had no instruction to approve. A review that found nothing is acceptable if it says what it checked. The one-page agent team log lists each agent, what it was allowed to see and do, what it recommended, what you decided, and where the evidence lives. Write it in your own voice; the rubric treats an agent-voiced log as missing authorship.

A small machine-playable interface
Implement these operations, or document an equivalent interface:

reset(seed)                 -> initial episode
    observe(player_id)          -> information that player is allowed to know
    legal_actions(player_id)    -> permitted actions, without unintended hints
    step(player_id, action)     -> validated transition and visible result
    outcome()                   -> ongoing / terminal, with reason and score
For hidden-information games, expose only information available to that role. A legal-action list can itself reveal a secret. Use an action vocabulary and validation feedback where that better matches your game design. Record the choice. For real-time games, a fixed-step wrapper lets an agent choose at bounded intervals without a model call every frame; declare the step size and the actions available per step.

The player receives no file-reading, shell, development or evaluator tools. The runner holds authoritative state . Prompts alone do not enforce this boundary. Each episode has a step limit, model-call limit, timeout policy, invalid-action handling and an explicit terminal reason. Count failed calls toward the budget. Never relabel a fallback move as a successful model move.

Compare players
Implement one cheap scripted, heuristic or search baseline and one model-driven player . Gemini, Anthropic and OpenAI models are equally eligible; other models may use an equivalent adapter. Use one live provider at minimum: your Google credit on Vertex AI ( gemini-3.5-flash-lite is enough), or an Anthropic or OpenAI key you already hold. ChatGPT Plus covers Codex while you build; it does not pay for the player's API calls. Comparing several providers is optional, with no grade advantage for spending more. Use the same observations and action rules for each player; disclose any asymmetric information or compute budget.

Declare a small suite before tuning. Normally use at least three distinct starting situations or tasks and two live trials per situation. Choose episodes short enough to fit the course budget; agree an equivalent reduced suite with the instructor if the game or access constraints require it. Reserve some cases or opponents from prompt tuning. Run the baseline on the same cases. A demonstration win alone is weak evidence .

Report completion or win/draw/loss counts, illegal actions, step/call limits, latency, token usage and estimated cost from dated prices. Include failures, trial counts, seeds, model and configuration identifiers, and game version. Do not imply statistical certainty from a small classroom sample. For partial-observation tasks, compare bounded history with an observation-only player; for fully observed games, test and explain whether memory helps. An explanation for omitting persistent memory is a legitimate design result.

For competitive games, self-play is useful alongside a different opponent or baseline. Single-player games use an automated solver. Self-play means playing against another instance of a policy; learning additionally requires a documented update to the policy, memory or parameters. An unchanged model repeatedly playing itself demonstrates behavior, not improvement by itself.

Deterministic CI checks rule invariants, legal/illegal actions, a successful path or terminal outcome , a genuine observed regression , and episode limits. Your checks run in the course repository through the one workflow file named for your login (see the hand-in steps). Mocked or replayed model outputs test the application. Fresh live trials test the current model. Human playtests remain necessary to judge clarity and fun; an agent's score cannot replace them. A model that judges its own play is not the sole grader.

Checkpoints and submission
Your Week 3 discussion header is the scope record of origin. If you change the game, design direction, or scope, update the scope statement in your README and post the change in your Week 3 thread so the current commitment is clear. Everything else lands in two in-class checkpoints and the submission. Checkpoints are formative and carry no separate grade; they are the evidence that your result was built in the order this brief describes.

Session 6, October 19: choose your design (classic or original) and your starting point (from scratch or an adapted codebase), write the scope statement, declare a suite of three situations, and start the interface wrapper in class. Bring your game's rule/source map and any codebase you plan to mod, with its reuse terms .
Session 7, October 26: the engine runs behind the five operations; the baseline completes an episode ; the model-driven player completes at least one live episode with a trace ; a first comparison table, however small; CI green on the deterministic checks.
Week of November 2 (no class): at least one human playtest of your build, by anyone you choose. Held-out cases , invalid actions, leakage, timeouts, and the recording.
Saturday November 7, 11:59 p.m.: submission on CourseWorks.
Before class November 16: silent-playtester notes, in the form of your Week 3 replies, on three assigned classmates' recordings: one thing you or an agent would have to guess, and the one question that removes the guess. Assignments go out at the November 9 session. These notes are the midterm's peer review; they count toward attendance and participation, and your midterm grade does not depend on them.
What you submit
One pull request to the course repository , columbia-university-ai-games/game-dev-f26Links to an external site. , targeting main . Put the complete project in midterms/<github-login>/ , using your lowercase GitHub login. For example, midterms/octocat/ . Include the game, executable player, baseline, tests, agent configurations , reports, and traces or trace links.
README.md in your folder , with setup, play, test, and evaluation commands that a TA can run from a fresh clone at your submitted commit. State the working directory for every command, starting from midterms/<github-login>/ . Include the scope statement, rule/source map with evidence labels ( design for your own rules), and source/reuse terms.
EVALUATION.md in your folder : the declared suite , comparison table, traces or links to them, CI evidence for this version of your game, and a limitations paragraph. Passing the starter's tests alone does not demonstrate that your game's rules and episode limits were tested.
AGENT-TEAM.md in your folder : the one-page agent team log .
A three-to-five-minute recording showing the game and an agent playing without manual move selection. Link it from both your README and the PR description, and make it viewable by the instructor, TAs, and assigned peer reviewers. A failed episode can be informative when accurately explained.
Human playtest notes from at least one session in which someone else, anyone (a classmate, friend, or family member), plays your build while you watch without helping. Put the notes in your folder or link them from its README: what the player did, where they hesitated or guessed, and what you changed or would change. Keep the player anonymous. If no playtest was possible, say so in your limitations paragraph, give the reason, and name what a playtest would have checked; check 5b then assesses that explanation in place of the notes.
Required hand-in steps
Work on a branch such as <github-login>/midterm , pushed to the course repository or your fork. Open one PR to the course repository , with only changes under your midterms/<github-login>/ folder plus one workflow file, .github/workflows/midterm-<github-login>.yml , that runs your folder's deterministic checks on pull requests touching that folder. That workflow is how check 3c is satisfied; a workflow that touches other folders or installs secrets fails the boundary check. Include the complete source and required artifacts in your folder; a link to a personal repository alone is not a submission. Keep each project's dependency manifests and configuration inside its folder.
In the PR description, state your GitHub login and project title, and link your folder's README, evaluation report, agent team log, playtest notes, and recording.
Submission time is the time of your last push to the PR branch before the deadline, as GitHub's timeline records it; the version at that push is what we grade. Pushes after the deadline are corrections and are not graded. If you want a later version graded instead, say so in the PR description; the submission time then becomes that push, and the late policy applies to the whole submission. Never force-push after the deadline. You do not need to name a commit; staff read it from the timeline, and the CourseWorks entry is checked against it.
Submit that PR's URL in the CourseWorks URL entry by the deadline. For example: https://github.com/columbia-university-ai-games/game-dev-f26/pull/123 . The PR must contain your completed submission and remain available for review. It does not have to be merged by the deadline; the instructor or a TA handles review and merging.
This is the required submission route for everyone. A personal-repository URL, tag URL, or archive upload does not satisfy the hand-in requirement. The course repository provides shared staff access; you do not need to invite the instructor or TAs to a separate project repository. If course repository access is blocking you, use the repository-access request formLinks to an external site. and contact a TA promptly.

The course repository is public. Include code and assets whose terms permit publication, credit your sources, and keep credentials, personal playtester data, and grades out of the PR. Keep installed dependencies, build caches, and large generated files out of the submission; document how to recreate or retrieve what is needed. The required game source and evidence must remain inspectable from the PR.

The midterm needs no Asana links; Asana begins with the final project at Session 8. Player-agent work replaces the former required NPC-memory/rewrite work; it adds no separate graded deliverable or new deadline.

Optional: the Handshake and OpenAI multiplayer game challenge
Handshake's AI Skills Studio runs a "Create a Multiplayer Game" mission with OpenAI; entries close October 30, 2026, 11:59 p.m. PT (the mission page says October 31; the official rules govern). The mission asks for a live multiplayer game at its own public URL that any group joins with a room code , no logins, no installs, built with ChatGPT Work mode. Judges score Execution, Creativity, Usefulness, and Polish at 25% each; the top twenty go to a panel and the top three win $1,000 each.

Entering is optional and earns no midterm credit. It fits the midterm when your game is a turn-based multiplayer game (a card game, a two-player board or pool game): the room-code version can share the engine if you keep an inspectable agent-evaluation version with the interface above. For other games, the contest is a separate project; do not let it displace the Session 6 and 7 checkpoints .

Read the official rulesLinks to an external site. before entering. Two terms matter: eligibility is limited to legal residents of the listed countries (the United States , Canada, the United Kingdom, most of Europe, India, and Caribbean territories) who are present there when they enter, and the rules do not define "legal resident" for students on visas; and entrants grant Handshake and OpenAI a perpetual license to display the submission and the entrant's name and likeness for promotion. The instructor cannot answer eligibility questions; Handshake can.

Resources and source use
Historical SourceLinks to an external site. : Infocom examples and other historical code . Check each game's provenance and reuse terms .
Artificial Intelligence and GamesLinks to an external site. : classical and contemporary methods for playing games.
Google Cloud Credits : redeeming your code, project setup, and setup_check .
Create a Multiplayer GameLinks to an external site. : the Handshake mission page.
Hoover Wargaming and Crisis Simulation Initiative CollectionLinks to an external site. : historical and contemporary games, including materials for playing and replication. An additional design resource, not a restriction on the game choices.
Credit the original designers and all sources. Public availability does not establish an open license. Link source materials and check their terms before copying code, prose or assets into a public repository. Use original assets where needed. The instructor resolves unclear publication rights before release, and decides check 1c for any submission whose reuse terms a TA flags as doubtful.

Rubric
The syllabus's five categories, 4 points each, 20 points. Each category lists its checks; the points table gives the shared scale; the guidance table that follows says what each score looks like for each check, so that two graders reading the same submission land on the same number. The submitted PR and commit, the evaluation report, the agent team log , the playtest notes, and the recording are assessed together.

Category	Full credit
Research & Critical Depth	(1a) The rule/source map labels every rule code, manual, observed , assumed, or design, with locators that distinguish inherited rules, inferred behavior, and your own specified choices. (1b) The completed midterm scope and its exclusions are explicit; omissions or adaptations of a reference game are named and explained where applicable. (1c) Sources are credited and reuse terms are checked and stated.
Game Design & AI Integration	(2a) The game plays its complete core loop to a clear ending or bounded episode . (2b) The model-driven player selects and submits actions through the observation/action interface , with no repository tools, answer key, or hidden state. (2c) The interface reveals only what that role may know, and the legal-action list leaks no secret.
Production / Engineering Quality	(3a) The game and player at the submitted commit run from the documented setup, play, and evaluation commands on a fresh clone. (3b) The runner holds authoritative state and enforces step, model-call, and timeout limits with explicit terminal reasons. (3c) CI checks rule invariants, legal and illegal actions, a terminal outcome , an observed regression , and episode limits. (3d) The configuration points to a working implementation agent , a reusable skill , and an independent review , in any assistant's form.
Creativity & Innovation	(4a) Design and engineering choices (rules, scope, action vocabulary, baseline , memory or history, evaluation suite) are purposeful and explained for either an original game or a reconstruction. (4b) The baseline is a real competitor for this game, and the experiment can distinguish the two players. A small game earns full credit through verified rules, a strong baseline, and a well-designed experiment; more scope earns no bonus.
Critical Reflection	(5a) The comparison is fair and reproducible: a suite declared before tuning, held-out cases , both players on the same cases, reporting outcomes, illegal actions, limits, latency, tokens, and dated cost , failures included. (5b) The agent team log and the limitations are in your voice, name the decisions you made, and use the human playtest notes or explain their omission. (5c) The recording shows the agent playing without manual move selection and states limits without overclaiming.
Points	Standard
4	Every check met clearly, with concrete evidence .
3	All checks attempted; one has a minor weakness and the central result is clear.
2	One check missing, or a substantial gap weakens the result or evidence.
1	An attempt, with little working or inspectable evidence.
0	Missing or cannot be assessed.