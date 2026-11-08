# Publication boundary

Publish only the clean main and cairn-mapper source branches. They must start with fresh history, not inherit the historical development repository. Keep the old repository and tested releases private and intact.

Run the audit on the index, working tree, and every reachable historical blob. Review the source manually as well: an extension scanner cannot determine whether prose or code reconstructs game content. Do not publish build/, disk images, memory, generated Inform, labels, transcripts, stories, archives, saves, or old history. Do not create release attachments from build outputs.

Before pushing, inspect git remote -v and the exact branch/commit set. Push only the intended source branches, never --mirror or --all from the old development repository. Verify the remote commits after publication. Technical checks do not confer permission to redistribute original content.
