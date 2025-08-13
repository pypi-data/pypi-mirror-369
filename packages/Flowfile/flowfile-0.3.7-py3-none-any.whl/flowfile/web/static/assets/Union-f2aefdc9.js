import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { d as defineComponent, r as ref, n as onMounted, R as nextTick, o as onUnmounted, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, g as createTextVNode, i as createCommentVNode, _ as _export_sfc, h as createBlock, a7 as Teleport } from "./index-f6c15e76.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "Union",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const showContextMenu = ref(false);
    const dataLoaded = ref(false);
    const nodeData = ref(null);
    const unionInput = ref({ mode: "relaxed" });
    const nodeUnion = ref(null);
    const loadNodeData = async (nodeId) => {
      var _a;
      console.log("loadNodeData from union ");
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodeUnion.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      if (nodeData.value) {
        if (nodeUnion.value) {
          if (nodeUnion.value.union_input) {
            unionInput.value = nodeUnion.value.union_input;
          } else {
            nodeUnion.value.union_input = unionInput.value;
          }
        }
      }
      dataLoaded.value = true;
      nodeStore.isDrawerOpen = true;
      console.log("loadNodeData from groupby");
    };
    const handleClickOutside = (event) => {
      const targetEvent = event.target;
      if (targetEvent.id === "pivot-context-menu")
        return;
      showContextMenu.value = false;
    };
    const pushNodeData = async () => {
      if (unionInput.value) {
        nodeStore.updateSettings(nodeUnion);
      }
      nodeStore.isDrawerOpen = false;
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    onMounted(async () => {
      await nextTick();
      window.addEventListener("click", handleClickOutside);
    });
    onUnmounted(() => {
      window.removeEventListener("click", handleClickOutside);
    });
    return (_ctx, _cache) => {
      return dataLoaded.value && nodeUnion.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeUnion.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => nodeUnion.value = $event)
        }, {
          default: withCtx(() => _cache[1] || (_cache[1] = [
            createTextVNode(" 'Union multiple tables into one table, this node does not have settings' ")
          ])),
          _: 1,
          __: [1]
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const Union_vue_vue_type_style_index_0_scoped_beb191a2_lang = "";
const readInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-beb191a2"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Union",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const childComp = ref(null);
    const props = __props;
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      drawer.value = false;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
    };
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      nodeStore.closeDrawer();
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        return;
      }
      if (childComp.value) {
        childComp.value.loadNodeData(props.nodeId);
        nodeStore.openDrawer(closeOnDrawer);
      }
    };
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "union.png",
          title: `${__props.nodeId}: Union data`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Union data",
            intro: "Union data into multiple tables. This node does not have settings"
          }),
          createVNode(readInput, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ], 512);
    };
  }
});
export {
  _sfc_main as default
};
