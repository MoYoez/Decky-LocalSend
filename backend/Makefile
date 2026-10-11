.PHONY: all build clean

SUBMODULE_DIR := localsend
WEB_DIR := $(SUBMODULE_DIR)/web
OUT_DIR := out
BINARY_NAME := localsend-core
# Target architectures; each produces $(BINARY_NAME)-<arch>
ARCHES ?= amd64 arm64

all: build

build:
	@if [ ! -f "$(SUBMODULE_DIR)/go.mod" ]; then \
		echo "localsend submodule missing. Run: git submodule update --init --recursive"; \
		exit 1; \
	fi
	mkdir -p "$(OUT_DIR)"
	mkdir -p "$(OUT_DIR)/web"
	@sudo pacman -Syyu --noconfirm
	@sudo pacman -Sy --noconfirm npm
	@for arch in $(ARCHES); do \
		echo "building $(BINARY_NAME)-$$arch"; \
		(cd "$(SUBMODULE_DIR)" && \
			CGO_ENABLED=0 GOOS=linux GOARCH=$$arch \
			go build -trimpath -ldflags "-s -w" -o "../$(OUT_DIR)/$(BINARY_NAME)-$$arch" .) || exit 1; \
	done
	@if [ -d "$(WEB_DIR)" ]; then \
		cd "$(WEB_DIR)" && \
		npm install && npm run build; \
		cd "$(CURDIR)" && cp -r "$(WEB_DIR)/out/" "$(OUT_DIR)/web/"; \
	fi

clean:
	rm -f $(addprefix $(OUT_DIR)/$(BINARY_NAME)-,$(ARCHES))