
DIALOGUE_FILE = new_dialogues.yaml
TITLE = hello
TEXT = Hello guys !

GROUP_FILE = new_group.yaml


.PHONY: new_all
new_all: $(DIALOGUE_FILE) $(GROUP_FILE)

$(DIALOGUE_FILE):
	@echo "# New" > $(DIALOGUE_FILE)
	@echo "" >> $(DIALOGUE_FILE)
	@echo "- category: \"dialogues\"" >> $(DIALOGUE_FILE)
	@echo "  dialogues:" >> $(DIALOGUE_FILE)
	@echo "    - title: \"$(TITLE)\"" >> $(DIALOGUE_FILE)
	@echo "      text: \"$(TEXT)\"" >> $(DIALOGUE_FILE)
	@echo "✅ Fichier YAML créé : $(DIALOGUE_FILE)"

$(GROUP_FILE):
	@echo "# New" > $(GROUP_FILE)
	@echo "" >> $(GROUP_FILE)
	@echo "- name: \"new_group\"" >> $(GROUP_FILE)
	@echo "  characters:" >> $(GROUP_FILE)
	@echo "    - name: \"a_name\"" >> $(GROUP_FILE)
	@echo "      voice_id: \"\"" >> $(GROUP_FILE)
	@echo "      gender: \"m\"" >> $(GROUP_FILE)
	@echo "✅ Fichier YAML créé : $(GROUP_FILE)"
	

readme:
	.venv/bin/silly-voice-lab

info:
	.venv/bin/silly-voice-lab info

run_dev:
	.venv/bin/silly-voice-lab run configs/dev_process.cfg
gen_dev:
	.venv/bin/silly-voice-lab gen configs/dev_process.cfg
run_text:
	.venv/bin/silly-voice-lab run configs/text_process.cfg
gen_text:
	.venv/bin/silly-voice-lab gen configs/text_process.cfg
run_prod:
	.venv/bin/silly-voice-lab run configs/prod_process.cfg
gen_prod:
	.venv/bin/silly-voice-lab gen configs/prod_process.cfg

run_all:
	.venv/bin/silly-voice-lab run configs/dev_process.cfg && \
	.venv/bin/silly-voice-lab run configs/text_process.cfg && \
	.venv/bin/silly-voice-lab run configs/prod_process.cfg

gen_all:
	.venv/bin/silly-voice-lab gen configs/dev_process.cfg && \
	.venv/bin/silly-voice-lab gen configs/text_process.cfg && \
	.venv/bin/silly-voice-lab gen configs/prod_process.cfg

