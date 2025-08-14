from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

EopfPayloadStoreParams = dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class EopfPayloadBreakpointStorageDict:
    storage: str
    store_params: EopfPayloadStoreParams


@dataclass(frozen=True, kw_only=True)
class EopfPayloadBreakpoint:
    """Breakpoint configuration

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    - "related_unit": reference name of the processing unit concern by this breakpoint
    - "break_mode": one of RETRIEVE SKIP RETRIEVE FORCE_WRITE.
    - "storage_dict": dictionary to setup the breakpoint products
        - "storage": uri to retrieve or write the breakpoint product
        - "store_params": parameters to give to the EOZarrStore

    """

    related_unit: str
    break_mode: Literal["RETRIEVE", "SKIP", "FORCE_WRITE"]
    storage: str
    storage_dict: EopfPayloadBreakpointStorageDict


@dataclass(frozen=True, kw_only=True)
class EopfPayloadWorkflowElement:
    """Represents the payload's Workflow

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    “active”: (optional) Allows to deactivate this step
    “step”: (information) Step number information, not used during processing
    “name”: identifier for the processing unit, can be used as related_unit in “breakpoints”
    “module”: string corresponding to the python path of the module (ex: “eopf.computing”)
    “processing_unit”: EOProcessingUnit class name (ex: “SumProcessor”)
    “inputs”: dict of product name or processing unit output identifier to use as inputs.
    “outputs”: dict of output product with their I/O output tu use.
    “adfs”: dict of adfs identifier to use.
    “parameters”: parameters to give to the processing unit at run time
    """

    active: bool | None = None
    step: Any | None = None
    name: str
    module: str
    processing_unit: str
    inputs: dict[str, str]
    outputs: dict[str, str]
    adfs: dict[str, str]
    parameters: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class EopfPayloadInputProductDescription:
    """Description of a Product, used in Inputs and Outputs IO part of the payload.

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    "id": name to give to EOProduct
    "path": uri or path (relative to the runner) to the product (ex: data/S3A_OL_1_EFR____NT_002.SEN3)
    "store_type": EOStoreFactory identifier of the store for the given product
    "store_params" : parameters of the store:
    """

    id: str
    path: str
    store_type: str  # probably 'zarr'
    store_params: EopfPayloadStoreParams


@dataclass(frozen=True, kw_only=True)
class EopfPayloadOutputProductDescription:
    """Description of a Product, used in Inputs and Outputs IO part of the payload.

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    “id”: name to give to EOProduct
    “path”: uri or path (relative to the runner) to the product (ex: data/S3A_OL_1_EFR____NT_002.SEN3)
    “store_type”: EOStoreFactory identifier of the store for the given product
    “store_params” : parameters of the store see the “store_params” section
    “type” : (optional, default to filename ) only for outputs. “filename” for a single product output.
    “folder” to retain multiple products underneath, default is to use the get_default_filename of each products.
    To use the eoproduct.name set “triggering__use_default_filename” to false in the configuration.
    “opening_mode” : (optional, default to CREATE). Specify the opening mode of the output product,
    only CREATE CREATE_OVERWRITE or UPDATE supported
    """

    id: str
    path: str
    store_type: str  # probably 'zarr'
    store_params: EopfPayloadStoreParams
    type: Literal["filename", "folder"] | None = None
    # opening_mode not available yet in eopf 1.5.2
    opening_mode: Literal["CREATE", "CREATE_OVERWRITE", "UPDATE"] | None = None


@dataclass(frozen=True, kw_only=True)
class EopfPayloadADFDescription:
    """Description of an ADF, used in the IO part of the payload.

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    "id": name to give to the ADF
    "path": uri or path (relative to the runner) to the product (ex: data/DEM.zarr)
    "store_params" : parameters of the store see the "store_params" section
    """

    id: str
    path: str
    store_params: EopfPayloadStoreParams


@dataclass(frozen=True, kw_only=True)
class EopfPayloadIO:
    """Configuration for Inputs and Outputs

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    "input_product" and "output_products" (only for "newproduct" mode):
    dictionary used to identify input (or output) product to use
    """

    input_products: list[EopfPayloadInputProductDescription] | None = None
    output_products: list[EopfPayloadOutputProductDescription] | None = None
    adfs: list[EopfPayloadADFDescription] | None = None


@dataclass(frozen=True, kw_only=True)
class EopfPayloadDaskContext:
    """Payload Dask Context

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    "cluster_type": type of dask cluster the should be used
    "cluster_config": configuration to pass direclty to the dask cluster constructor.
    For example to the dask.distributed.LocalCluster constructor
    "client_config": configuration to pass directly to the Client
    "performance_report_file": Dask performance report file to write to for ex ‘report.html’
    see https://distributed.dask.org/en/latest/diagnosing-performance.html
    """

    cluster_type: str
    cluster_config: dict[str, Any]
    client_config: dict[str, Any]
    performance_report_file: str


@dataclass(frozen=True, kw_only=True)
class EopfPayload:
    """Represents a Payload for the EOPF to be ran

    See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/develop/orchestration-guide/triggering.html

    general_configuration
        (optional) Add configuration elements to the EOConfiguration to configure the software behaviour.
        The priority policy of parameters is this one :
        config_files > general_configuration > env variables starting with EOPF_
        Example of parameters:
            * "logging" :
        Some triggering parameters are also available:
            * "triggering__use_basic_logging" : setup a basic logging configuration, usefull if you don't
                have logging configuration files
            * "triggering__validate_run" : Activate the validation around the run method
            * "triggering__use_default_filename" : Use get_default_filename on eoproduct to construct the path
                in case of "folder" output, else use eoproduct.name
            * "triggering__load_default_logging" : Load the default EOPF logging configuration files installed
                allong the software
            * "triggering__wait_before_exit" : Wait this time before exit dask context etc,
                in order to access the dask dashboard in case of localCluster
            * "dask__export_graphs" :
                Export the dask graph for variables at writing time
    breakpoints
        (optional) configure the breakpoint component Intermediate Output - BreakPoint Object
    workflow
        item or list of workflow elements
    io
        configuration for inputs and outputs
    dask_context
        (optional) configuration for DaskContext
    logging
        (optional) list of configuration files for EOLogging.
    config
        (optional) list of configuration files for EOConfiguration.

    """

    general_configuration: dict[str, Any] | None = None
    breakpoints: list[EopfPayloadBreakpoint] | None = None
    workflow: list[EopfPayloadWorkflowElement] | EopfPayloadWorkflowElement
    io: EopfPayloadIO
    dask_context: EopfPayloadDaskContext | None = None
    logging: list[str] | None = None
    config: list[str] | None = None


def convert_payload_dataclass_to_dict(payload: EopfPayload) -> dict[str, Any]:
    payload_dict = asdict(payload)
    payload_dict["I/O"] = payload_dict.pop("io")
    return payload_dict


def convert_payload_dict_to_dataclass(payload_dict: dict[str, Any]) -> EopfPayload:
    breakpoints_orig = payload_dict["breakpoints"]
    if breakpoints_orig is None:
        breakpoints = None
    else:
        breakpoints = [EopfPayloadBreakpoint(**bp) for bp in breakpoints_orig]
    payload = EopfPayload(
        config=payload_dict["config"],
        general_configuration=payload_dict["general_configuration"],
        breakpoints=breakpoints,
        workflow=[EopfPayloadWorkflowElement(**wf) for wf in payload_dict["workflow"]],
        io=EopfPayloadIO(
            # modification_mode=payload_dict["I/O"]["modification_mode"],
            input_products=[EopfPayloadInputProductDescription(**pr) for pr in payload_dict["I/O"]["input_products"]],
            output_products=[
                EopfPayloadOutputProductDescription(**pr) for pr in payload_dict["I/O"]["output_products"]
            ],
            adfs=[EopfPayloadADFDescription(**pr) for pr in payload_dict["I/O"]["adfs"]],
        ),
        logging=payload_dict["logging"],
        dask_context=EopfPayloadDaskContext(**payload_dict["dask_context"]),
    )
    return payload


def render_dot_diagram_from_payload(
    payload: EopfPayload,
    *,
    orientation: Literal["LR", "TB", "RL", "BT"] = "LR",
) -> str:
    return _render_dot_diagram(payload, orientation=orientation)


def _render_dot_diagram(payload: EopfPayload, *, orientation: Literal["LR", "TB", "RL", "BT"] = "LR") -> str:
    # Inputs
    rendered_input_section = _render_dot_inputs(payload)

    # Output
    rendered_output_section = _render_dot_output(payload)

    # Processor
    workflow = payload.workflow if isinstance(payload.workflow, list) else [payload.workflow]
    rendered_processor = _render_dot_processor(workflow)

    # Final output link
    rendered_final_output_link = _render_dot_final_output_link(payload, workflow)

    # Breakpoints
    rendered_breakpoint_section = _render_dot_breakpoint_section(payload)

    return f"""
digraph G {{

rankdir = "{orientation}";

fontname="Courier";
node [fontname="Courier"]
edge [fontname="Courier"]

{rendered_input_section}

{rendered_output_section}

{rendered_processor}

{rendered_final_output_link}

{rendered_breakpoint_section}

}}

""".strip()


def _render_dot_breakpoint_section(payload: EopfPayload) -> str:
    if payload.breakpoints is None or len(payload.breakpoints) == 0:
        rendered_breakpoint_section = "%% No breakpoints provided in the payload."
    else:
        rendered_breakpoints = "\n".join(_render_dot_breakpoint(bp) for bp in payload.breakpoints)
        rendered_breakpoint_section = f"""
// Breakpoints
subgraph cluster_Breakpoints {{
label="Breakpoints";
style=filled;
color=lightgrey;
node [color=black, style=filled, fillcolor=white, shape=box3d];
edge [style=dashed];

{rendered_breakpoints}
}}

""".strip()

    return rendered_breakpoint_section


def _render_dot_breakpoint(bp: EopfPayloadBreakpoint) -> str:
    return f'"{bp.related_unit}" -> "{Path(bp.storage).name}" [ label="breakpoint {bp.break_mode}" ];'


def _render_dot_final_output_link(
    payload: EopfPayload,
    workflow: list[EopfPayloadWorkflowElement],
) -> str:
    if payload.io.output_products is None or len(workflow) == 0:
        rendered_final_output_link = "%% No workflow or output product provided in the payload."
    else:
        last_processor = workflow[-1]
        # Note: only supports one product!
        final_output_link = f'"{last_processor.name}" -> "{payload.io.output_products[0].id}";'
        rendered_final_output_link = f"""
// Final output link
{final_output_link}
""".strip()

    return rendered_final_output_link


def _render_dot_processor(workflow: list[EopfPayloadWorkflowElement]) -> str:
    if len(workflow) == 0:
        rendered_processor = "%% No workflow provided in the payload."
    else:
        rendered_processor_links = "\n".join(_render_dot_processing_unit(processor) for processor in workflow)
        rendered_processor = f"""
// Processor
subgraph cluster_Processor {{
label="Processor";
style=filled;
color=lightgrey;
node [color=black, style=filled, fillcolor=white, shape=box3d];

{rendered_processor_links}
}}
""".strip()

    return rendered_processor


def _render_dot_processing_unit(processor: EopfPayloadWorkflowElement) -> str:
    return "\n".join(f'"{input_}" -> "{processor.name}";' for input_ in processor.inputs)


def _render_dot_output(payload: EopfPayload) -> str:
    if payload.io.output_products is None:
        rendered_output_section = "%% No output product provided in the payload."
    else:
        # Note: only supports one product!
        rendered_output = f'"{payload.io.output_products[0].id}";'
        rendered_output_section = f"""
// Output
subgraph cluster_Output {{
label="Output";
style=filled;
color=lightgrey;
node [color=black, style=filled, fillcolor=white, shape=folder];

{rendered_output}
}}
""".strip()

    return rendered_output_section


def _render_dot_inputs(payload: EopfPayload) -> str:
    if payload.io.input_products is None:
        rendered_input_section = "%% No input products provided in the payload."
    else:
        rendered_inputs = "\n".join(f'"{i.id}";' for i in payload.io.input_products)
        rendered_input_section = f"""
// Inputs
subgraph cluster_Inputs {{
label="Inputs";
style=filled;
color=lightgrey;
node [color=black, style=filled, fillcolor=white, shape=folder];

{rendered_inputs}
}}
""".strip()

    return rendered_input_section


def render_mermaid_diagram_from_payload(payload: EopfPayload, *, orientation: Literal["LR", "TB"] = "LR") -> str:
    return _render_mermaid_diagram(payload, orientation=orientation)


def _render_mermaid_diagram(payload: EopfPayload, *, orientation: Literal["LR", "TB"] = "LR") -> str:
    # Inputs
    rendered_input_section = _render_mermaid_inputs(payload)

    # Output
    rendered_output_section = _render_mermaid_output(payload)

    # Processor
    workflow = payload.workflow if isinstance(payload.workflow, list) else [payload.workflow]
    rendered_processor = _render_mermaid_processor(workflow)

    # Final output link
    rendered_final_output_link = _render_mermaid_final_output_link(payload, workflow)

    # Breakpoints
    rendered_breakpoint_section = _render_mermaid_breakpoint_section(payload)

    return f"""
flowchart {orientation}

{rendered_input_section}

{rendered_processor}

{rendered_final_output_link}

{rendered_breakpoint_section}

{rendered_output_section}
""".strip()


def _render_mermaid_breakpoint_section(payload: EopfPayload) -> str:
    if payload.breakpoints is None or len(payload.breakpoints) == 0:
        rendered_breakpoint_section = "%% No breakpoints provided in the payload."
    else:
        rendered_breakpoints = "\n".join(
            f"{bp.related_unit} -. breakpoint {bp.break_mode} .-> {Path(bp.storage).name}" for bp in payload.breakpoints
        )
        rendered_breakpoint_section = f"""
%% Breakpoints
subgraph Breakpoints
{rendered_breakpoints}
end
""".strip()

    return rendered_breakpoint_section


def _render_mermaid_final_output_link(
    payload: EopfPayload,
    workflow: list[EopfPayloadWorkflowElement],
) -> str:
    if payload.io.output_products is None or len(workflow) == 0:
        rendered_final_output_link = "%% No workflow or output product provided in the payload."
    else:
        last_processor = workflow[-1]
        # Note: only supports one product!
        final_output_link = f"{last_processor.name} --> {payload.io.output_products[0].id}"
        rendered_final_output_link = f"""
%% Final output link
{final_output_link}
""".strip()

    return rendered_final_output_link


def _render_mermaid_processor(workflow: list[EopfPayloadWorkflowElement]) -> str:
    if len(workflow) == 0:
        rendered_processor = "%% No workflow provided in the payload."
    else:
        rendered_processor_links = "\n".join(_render_mermaid_processing_unit(processor) for processor in workflow)
        rendered_processor = f"""
%% Processor
subgraph Processor
{rendered_processor_links}
end
""".strip()

    return rendered_processor


def _render_mermaid_processing_unit(processor: EopfPayloadWorkflowElement) -> str:
    return "\n".join(f"{input_} --> {processor.name}" for input_ in processor.inputs)


def _render_mermaid_output(payload: EopfPayload) -> str:
    if payload.io.output_products is None:
        rendered_output_section = "%% No output product provided in the payload."
    else:
        # Note: only supports one product!
        rendered_output = payload.io.output_products[0].id
        rendered_output_section = f"""
%% Output
subgraph Output
{rendered_output}
end
""".strip()

    return rendered_output_section


def _render_mermaid_inputs(payload: EopfPayload) -> str:
    if payload.io.input_products is None:
        rendered_input_section = "%% No input products provided in the payload."
    else:
        rendered_inputs = "\n".join(f"{i.id}" for i in payload.io.input_products)
        rendered_input_section = f"""
%% Inputs
subgraph Inputs
{rendered_inputs}
end
""".strip()

    return rendered_input_section
