// /static/js/toaster.js

const ToastManager = (() => {
    const MAX_VISIBLE = 5;

    const toasts = [];

    const TYPE_CLASS = {
        info: "toast--info",
        success: "toast--success",
        warning: "toast--warning",
        error: "toast--error",
        default: "",
    };

    function getContainer() {
        let container = document.getElementById("notifications");
        if (!container) {
            container = document.createElement("div");
            container.id = "notifications";
            document.body.appendChild(container);
        }
        return container;
    }
    function animateStackChange(container, firstHeight) {
        const motionOK = window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
        if (!motionOK) return;

        const last = container.offsetHeight;
        const invert = last - firstHeight;
        if (!invert) return;

        container.animate([{ transform: `translateY(${invert}px)` }, { transform: "translateY(0)" }], {
            duration: 180,
            easing: "ease-out",
        });
    }

    function removeToast(record) {
        if (!record || !record.el) return;
        const el = record.el;

        if (record.timeoutId != null) {
            clearTimeout(record.timeoutId);
        }

        el.classList.add("toast--hiding");
        el.classList.remove("toast--visible");

        const onTransitionEnd = (e) => {
            if (e.target !== el) return;
            el.removeEventListener("transitionend", onTransitionEnd);
            if (el.parentElement) {
                el.parentElement.removeChild(el);
            }
        };

        el.addEventListener("transitionend", onTransitionEnd);

        const idx = toasts.indexOf(record);
        if (idx !== -1) {
            toasts.splice(idx, 1);
        }
    }

    function enforceMaxVisible() {
        const visibleToasts = toasts.filter((t) => !t.ignoreOverflow);
        const overflow = visibleToasts.length - MAX_VISIBLE;
        if (overflow <= 0) return;

        for (let i = 0; i < overflow; i++) {
            const record = visibleToasts[i];
            removeToast(record);
        }
    }

    /**
     * Создает уведомление.
     * @param {Object} options
     * @param {string} options.title
     * @param {string} [options.message]
     * @param {'info'|'success'|'warning'|'error'} [options.type='info']
     * @param {number} [options.duration=5000]
     * @param {boolean} [options.persistent=false]
     * @param {boolean} [options.disableClose=false]
     * @param {(toastEl: HTMLElement) => void} [options.onCloseClick]
     * @param {boolean} [options.closeAfterCallback=true]
     * @param {string} [options.toastClass]        // кастомные классы на корне
     * @param {string} [options.headerClass]       // на .toast-header
     * @param {string} [options.titleClass]        // на .toast-title
     * @param {string} [options.bodyClass]         // на .toast-body
     * @param {string} [options.closeButtonClass]  // на кнопку закрытия
     * @returns {HTMLElement}
     */
    function createToast(options) {
        const {
            title,
            message = "",
            type = "info",
            duration = 5000,
            persistent = false,
            disableClose = false,
            onCloseClick = null,
            closeAfterCallback = true,
            toastClass = "",
            headerClass = "",
            titleClass = "",
            bodyClass = "",
            closeButtonClass = "",
        } = options || {};

        if (!title) {
            throw new Error("Toast title is required");
        }

        const container = getContainer();

        const toastEl = document.createElement("div");
        toastEl.className = `toast ${TYPE_CLASS[type] || TYPE_CLASS.default} ${toastClass}`.trim();

        const headerEl = document.createElement("div");
        headerEl.className = `toast-header ${headerClass}`.trim();

        const titleEl = document.createElement("div");
        titleEl.className = `toast-title ${titleClass}`.trim();
        titleEl.textContent = title;

        headerEl.appendChild(titleEl);

        if (!disableClose) {
            const closeBtn = document.createElement("button");
            closeBtn.type = "button";
            closeBtn.className = `toast-close ${closeButtonClass}`.trim();
            closeBtn.innerHTML = "&times;";

            closeBtn.addEventListener("click", (e) => {
                e.stopPropagation();

                if (typeof onCloseClick === "function") {
                    onCloseClick(toastEl);
                    if (closeAfterCallback) {
                        const record = toasts.find((t) => t.el === toastEl);
                        if (record) removeToast(record);
                    }
                } else {
                    const record = toasts.find((t) => t.el === toastEl);
                    if (record) removeToast(record);
                }
            });

            headerEl.appendChild(closeBtn);
        }

        toastEl.appendChild(headerEl);

        if (message) {
            const bodyEl = document.createElement("div");
            bodyEl.className = `toast-body ${bodyClass}`.trim();
            bodyEl.textContent = message;
            toastEl.appendChild(bodyEl);
        }
        const firstHeight = container.offsetHeight;

        container.appendChild(toastEl);

        if (container.children.length > 1) {
            animateStackChange(container, firstHeight);
        }

        const record = {
            el: toastEl,
            timeoutId: null,
            ignoreOverflow: !!persistent,
        };
        toasts.push(record);

        if (!record.ignoreOverflow) {
            enforceMaxVisible();
        }

        // ПОСЛЕ container.appendChild(toastEl);

        requestAnimationFrame(() => {
            toastEl.classList.remove("toast--hiding", "toast--visible");
            void toastEl.offsetWidth; // форсируем reflow
            requestAnimationFrame(() => {
                toastEl.classList.add("toast--visible");
            });
        });

        if (!persistent && duration > 0) {
            record.timeoutId = window.setTimeout(() => {
                removeToast(record);
            }, duration);
        }

        return toastEl;
    }

    return {
        createToast,
    };
})();

window.createToast = ToastManager.createToast;
