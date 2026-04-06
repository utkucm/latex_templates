.PHONY: all assignments lecture_notes research_statement cv clean

LATEXMK = latexmk -pdf -interaction=nonstopmode

all: assignments lecture_notes research_statement cv

assignments:
	cd assignments && $(LATEXMK) main.tex

lecture_notes:
	cd lecture_notes && $(LATEXMK) main.tex

research_statement:
	cd research_statement && $(LATEXMK) main.tex

cv:
	cd cv && $(LATEXMK) main.tex

clean:
	cd assignments && latexmk -C main.tex
	cd lecture_notes && latexmk -C main.tex
	cd research_statement && latexmk -C main.tex
	cd cv && latexmk -C main.tex
