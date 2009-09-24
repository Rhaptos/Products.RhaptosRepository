i18ndude extract-literals --pot RisaRepository.pot > manual.pot
i18ndude rebuild-pot --pot RisaRepository.pot --merge manual.pot ../skins/
