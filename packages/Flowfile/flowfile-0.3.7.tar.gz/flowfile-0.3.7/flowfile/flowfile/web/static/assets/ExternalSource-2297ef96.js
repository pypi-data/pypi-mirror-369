import { C as CodeLoader } from "./vue-content-loader.es-0371da73.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { d as defineComponent, r as ref, a3 as watchEffect, b as resolveComponent, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, F as Fragment, q as renderList, i as createCommentVNode, h as createBlock, u as unref, _ as _export_sfc, n as onMounted, R as nextTick, a7 as Teleport } from "./index-f6c15e76.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
function get_template_source_type(type, options) {
  switch (type) {
    case "SAMPLE_USERS":
      return {
        SAMPLE_USERS: true,
        size: (options == null ? void 0 : options.size) || 100,
        // Default size is 100 if not provided
        orientation: (options == null ? void 0 : options.orientation) || "row",
        // Default orientation is 'ROWS'
        fields: []
      };
    default:
      throw new Error("Unsupported configuration type");
  }
}
const _hoisted_1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = {
  key: 0,
  class: "file-upload-container"
};
const _hoisted_3 = {
  key: 0,
  class: "file-upload-wrapper"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "ExternalSource",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const sampleUsers = ref(null);
    const nodeExternalSource = ref(null);
    const dataLoaded = ref(false);
    const typeSelected = ref(false);
    const writingOptions = ["sample_users"];
    const selectedExternalSource = ref(null);
    const isDirty = ref(false);
    watchEffect(() => {
    });
    const loadNodeData = async (nodeId) => {
      var _a, _b, _c;
      const nodeResult = await nodeStore.getNodeData(nodeId, false);
      nodeExternalSource.value = nodeResult == null ? void 0 : nodeResult.setting_input;
      if ((_a = nodeExternalSource.value) == null ? void 0 : _a.is_setup) {
        if (((_b = nodeExternalSource.value) == null ? void 0 : _b.identifier) == "sample_users") {
          sampleUsers.value = (_c = nodeExternalSource.value) == null ? void 0 : _c.source_settings;
          selectedExternalSource.value = "sample_users";
        }
      }
      typeSelected.value = true;
      dataLoaded.value = true;
      isDirty.value = false;
    };
    const loadTemplateValue = () => {
      console.log(selectedExternalSource.value);
      if (selectedExternalSource.value === "sample_users") {
        sampleUsers.value = get_template_source_type("SAMPLE_USERS");
        if (nodeExternalSource.value) {
          nodeExternalSource.value.source_settings = sampleUsers.value;
        }
        isDirty.value = true;
      }
      typeSelected.value = true;
      if (nodeExternalSource.value && selectedExternalSource.value) {
        nodeExternalSource.value.identifier = selectedExternalSource.value;
      }
    };
    const pushNodeDataAction = async () => {
      if (nodeExternalSource.value && isDirty.value) {
        nodeExternalSource.value.is_setup = true;
        nodeExternalSource.value.source_settings.fields = [];
        isDirty.value = false;
      }
      await nodeStore.updateSettings(nodeExternalSource);
      if (nodeExternalSource.value) {
        await nodeStore.getNodeData(Number(nodeExternalSource.value.node_id), false);
      }
    };
    const pushNodeData = async () => {
      dataLoaded.value = false;
      if (nodeExternalSource.value) {
        if (isDirty.value || nodeExternalSource.value.identifier) {
          await pushNodeDataAction();
        }
      }
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_option = resolveComponent("el-option");
      const _component_el_select = resolveComponent("el-select");
      return dataLoaded.value && nodeExternalSource.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeExternalSource.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeExternalSource.value = $event)
        }, {
          default: withCtx(() => [
            _cache[2] || (_cache[2] = createBaseVNode("div", { class: "listbox-subtitle" }, "Select the type of external source", -1)),
            createVNode(_component_el_select, {
              modelValue: selectedExternalSource.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => selectedExternalSource.value = $event),
              class: "m-2",
              placeholder: "Select type of external source",
              size: "small",
              onChange: loadTemplateValue
            }, {
              default: withCtx(() => [
                (openBlock(), createElementBlock(Fragment, null, renderList(writingOptions, (item) => {
                  return createVNode(_component_el_option, {
                    key: item,
                    label: item,
                    value: item
                  }, null, 8, ["label", "value"]);
                }), 64))
              ]),
              _: 1
            }, 8, ["modelValue"]),
            typeSelected.value ? (openBlock(), createElementBlock("div", _hoisted_2, [
              selectedExternalSource.value === "sample_users" && sampleUsers.value ? (openBlock(), createElementBlock("div", _hoisted_3)) : createCommentVNode("", true)
            ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }))
          ]),
          _: 1,
          __: [2]
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const ExternalSource_vue_vue_type_style_index_0_scoped_62f1d8e0_lang = "";
const externalSource = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-62f1d8e0"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ExternalSource",
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
    const el = ref(null);
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
      drawer.value = false;
      nodeStore.isDrawerOpen = false;
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
      return openBlock(), createElementBlock("div", {
        ref_key: "el",
        ref: el
      }, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "external_source.png",
          title: `${__props.nodeId}: External source`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "External source",
            intro: "Import data from an external source"
          }),
          createVNode(externalSource, {
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
