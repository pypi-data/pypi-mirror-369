import { g as getImageUrl } from "./designer-13eabd83.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { d as defineComponent, r as ref, l as computed, n as onMounted, m as watch, R as nextTick, c as openBlock, e as createElementBlock, p as createBaseVNode, t as toDisplayString, s as normalizeClass, u as unref, _ as _export_sfc, b as resolveComponent, h as createBlock, w as withCtx, f as createVNode } from "./index-f6c15e76.js";
const _hoisted_1$1 = { class: "component-wrapper" };
const _hoisted_2$1 = { class: "tooltip-text" };
const _hoisted_3$1 = ["src", "alt"];
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "nodeButton",
  props: {
    nodeId: { type: Number, required: true },
    imageSrc: { type: String, required: true },
    title: { type: String, required: true }
  },
  emits: ["click"],
  setup(__props, { emit: __emit }) {
    const description = ref("");
    const mouseX = ref(0);
    const mouseY = ref(0);
    const nodeStore = useNodeStore();
    const props = __props;
    const isSelected = computed(() => {
      return nodeStore.node_id == props.nodeId;
    });
    computed(() => {
      const overlayWidth = 400;
      const overlayHeight = 200;
      const buffer = 100;
      let left = mouseX.value + buffer;
      let top = mouseY.value + buffer;
      if (left + overlayWidth > window.innerWidth) {
        left -= overlayWidth + 2 * buffer;
      }
      if (top + overlayHeight > window.innerHeight) {
        top -= overlayHeight + 2 * buffer;
      }
      left = Math.max(left, buffer);
      top = Math.max(top, buffer);
      return {
        top: `${top}px`,
        left: `${left}px`
      };
    });
    const nodeResult = computed(() => {
      const nodeResult2 = nodeStore.getNodeResult(props.nodeId);
      const nodeValidation = nodeStore.getNodeValidation(props.nodeId);
      if (nodeResult2 && nodeResult2.is_running) {
        return {
          success: void 0,
          statusIndicator: "running",
          hasRun: false,
          error: void 0
        };
      }
      if (nodeResult2 && !nodeResult2.is_running) {
        if (nodeValidation) {
          if (nodeResult2.success === true && !nodeValidation.isValid && nodeValidation.validationTime > nodeResult2.start_timestamp) {
            return {
              success: true,
              statusIndicator: "warning",
              error: nodeValidation.error,
              hasRun: true
            };
          }
          if (nodeResult2.success === true && nodeValidation.isValid) {
            return {
              success: true,
              statusIndicator: "success",
              error: nodeResult2.error || nodeValidation.error,
              hasRun: true
            };
          }
          if (nodeResult2.success === false && nodeValidation.isValid && nodeValidation.validationTime > nodeResult2.start_timestamp) {
            return {
              success: false,
              statusIndicator: "unknown",
              error: nodeResult2.error || nodeValidation.error,
              hasRun: true
            };
          }
          if (nodeResult2.success === false && (!nodeValidation.isValid || !nodeValidation.validationTime)) {
            return {
              success: false,
              statusIndicator: "failure",
              error: nodeResult2.error || nodeValidation.error,
              hasRun: true
            };
          }
        }
        return {
          success: nodeResult2.success ?? false,
          statusIndicator: nodeResult2.success ? "success" : "failure",
          error: nodeResult2.error,
          hasRun: true
        };
      }
      if (nodeValidation) {
        if (!nodeValidation.isValid) {
          return {
            success: false,
            statusIndicator: "warning",
            error: nodeValidation.error,
            hasRun: false
          };
        }
        if (nodeValidation.isValid) {
          return {
            success: true,
            statusIndicator: "unknown",
            error: nodeValidation.error,
            hasRun: false
          };
        }
      }
      return void 0;
    });
    const tooltipContent = computed(() => {
      var _a, _b, _c;
      switch ((_a = nodeResult.value) == null ? void 0 : _a.statusIndicator) {
        case "success":
          return "Operation successful";
        case "failure":
          return "Operation failed: \n" + (((_b = nodeResult.value) == null ? void 0 : _b.error) || "No error message available");
        case "warning":
          return "Operation warning: \n" + (((_c = nodeResult.value) == null ? void 0 : _c.error) || "No warning message available");
        case "running":
          return "Operation in progress...";
        case "unknown":
        default:
          return "Status unknown";
      }
    });
    const getNodeDescription = async () => {
      description.value = await nodeStore.getNodeDescription(props.nodeId);
    };
    const emits = __emit;
    const onClick = () => {
      emits("click");
    };
    onMounted(() => {
      watch(
        () => props.nodeId,
        async (newVal) => {
          if (newVal !== -1) {
            await nextTick();
            getNodeDescription();
          }
        }
      );
    });
    return (_ctx, _cache) => {
      var _a;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createBaseVNode("div", {
          class: normalizeClass(["status-indicator", (_a = nodeResult.value) == null ? void 0 : _a.statusIndicator])
        }, [
          createBaseVNode("span", _hoisted_2$1, toDisplayString(tooltipContent.value), 1)
        ], 2),
        createBaseVNode("button", {
          class: normalizeClass(["node-button", { selected: isSelected.value }]),
          onClick
        }, [
          createBaseVNode("img", {
            src: unref(getImageUrl)(props.imageSrc),
            alt: props.title,
            width: "50"
          }, null, 8, _hoisted_3$1)
        ], 2)
      ]);
    };
  }
});
const nodeButton_vue_vue_type_style_index_0_scoped_a984e3d6_lang = "";
const NodeButton = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-a984e3d6"]]);
const _hoisted_1 = { class: "listbox-wrapper" };
const _hoisted_2 = { class: "listbox-title" };
const _hoisted_3 = { class: "intro-content" };
const _hoisted_4 = {
  key: 1,
  class: "title"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "nodeTitle",
  props: {
    title: {
      type: String,
      required: true
    },
    intro: {
      type: String,
      required: false,
      default: ""
      // Add default value to resolve warning
    }
  },
  setup(__props) {
    const props = __props;
    return (_ctx, _cache) => {
      const _component_el_collapse_item = resolveComponent("el-collapse-item");
      const _component_el_collapse = resolveComponent("el-collapse");
      return openBlock(), createElementBlock("div", _hoisted_1, [
        props.intro ? (openBlock(), createBlock(_component_el_collapse, {
          key: 0,
          class: "listbox-expandable"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_collapse_item, null, {
              title: withCtx(() => [
                createBaseVNode("div", _hoisted_2, toDisplayString(props.title), 1)
              ]),
              default: withCtx(() => [
                createBaseVNode("div", _hoisted_3, toDisplayString(props.intro), 1)
              ]),
              _: 1
            })
          ]),
          _: 1
        })) : (openBlock(), createElementBlock("div", _hoisted_4, toDisplayString(props.title), 1))
      ]);
    };
  }
});
const nodeTitle_vue_vue_type_style_index_0_scoped_0db5c358_lang = "";
const NodeTitle = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-0db5c358"]]);
export {
  NodeButton as N,
  NodeTitle as a
};
