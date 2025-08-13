import { d as defineComponent, c as openBlock, e as createElementBlock, p as createBaseVNode, F as Fragment, q as renderList, s as normalizeClass, t as toDisplayString, T as normalizeStyle, _ as _export_sfc, g as createTextVNode, i as createCommentVNode } from "./index-f6c15e76.js";
const _hoisted_1$1 = ["onClick"];
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "ContextMenu",
  props: {
    position: { type: Object, required: true },
    options: {
      type: Array,
      required: true
    }
  },
  emits: ["select", "close"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const selectOption = (action) => {
      emit("select", action);
      emit("close");
    };
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        class: "context-menu",
        style: normalizeStyle({ top: __props.position.y + "px", left: __props.position.x + "px" })
      }, [
        createBaseVNode("ul", null, [
          (openBlock(true), createElementBlock(Fragment, null, renderList(__props.options, (option) => {
            return openBlock(), createElementBlock("li", {
              key: option.action,
              class: normalizeClass({ disabled: option.disabled }),
              onClick: ($event) => !option.disabled && selectOption(option.action)
            }, toDisplayString(option.label), 11, _hoisted_1$1);
          }), 128))
        ])
      ], 4);
    };
  }
});
const ContextMenu_vue_vue_type_style_index_0_scoped_a562ba5e_lang = "";
const ContextMenu = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-a562ba5e"]]);
const _hoisted_1 = { class: "listbox-wrapper" };
const _hoisted_2 = { class: "listbox-row" };
const _hoisted_3 = { class: "listbox-subtitle" };
const _hoisted_4 = { class: "items-container" };
const _hoisted_5 = { key: 0 };
const _hoisted_6 = ["onClick"];
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "SettingsSection",
  props: {
    title: { type: String, required: true },
    items: { type: Array, required: true }
  },
  emits: ["removeItem"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const emitRemove = (item) => {
      emit("removeItem", item);
    };
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, toDisplayString(__props.title), 1),
          createBaseVNode("div", _hoisted_4, [
            (openBlock(true), createElementBlock(Fragment, null, renderList(__props.items, (item, index) => {
              return openBlock(), createElementBlock("div", {
                key: index,
                class: "item-box"
              }, [
                item !== "" ? (openBlock(), createElementBlock("div", _hoisted_5, [
                  createTextVNode(toDisplayString(item) + " ", 1),
                  createBaseVNode("span", {
                    class: "remove-btn",
                    onClick: ($event) => emitRemove(item)
                  }, "x", 8, _hoisted_6)
                ])) : createCommentVNode("", true)
              ]);
            }), 128))
          ])
        ])
      ]);
    };
  }
});
const SettingsSection_vue_vue_type_style_index_0_scoped_89e3a043_lang = "";
const SettingsSection = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-89e3a043"]]);
export {
  ContextMenu as C,
  SettingsSection as S
};
