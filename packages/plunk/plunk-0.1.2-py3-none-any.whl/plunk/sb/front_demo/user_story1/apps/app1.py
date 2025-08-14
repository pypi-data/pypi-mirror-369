"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from typing import Mapping
from know.boxes import *
from functools import partial
from typing import Callable, Iterable
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from i2 import Pipe, Sig
from front.crude import Crudifier, prepare_for_crude_dispatch
from lined import LineParametrized
import numpy as np

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    KwargsInput,
    PipelineMaker,
)
from streamlitfront.elements import (
    AudioRecorder,
    FileUploader,
    MultiSourceInput,
)
import streamlit as st
from plunk.sb.front_experiments.streamlitfront_dataprep.data_prep2 import (
    # DFLT_WF_PATH,
    # DFLT_ANNOT_PATH,
    data_from_wav_folder,
)
import soundfile as sf
from io import BytesIO
import matplotlib.pyplot as plt
from plunk.sb.front_demo.user_story1.components.components import (
    AudioArrayDisplay,
    GraphOutput,
    ArrayPlotter,
)
from plunk.sb.front_demo.user_story1.utils.tools import (
    DFLT_CHUNKER,
    DFLT_FEATURIZER,
    DFLT_CHK_SIZE,
    chunker,
    featurizer,
    WaveForm,
    Stroll,
    clean_dict,
    scores_to_intervals,
    pyplot_with_intervals,
)

# DFLT_FEATURIZER = lambda chk: np.abs(np.fft.rfft(chk))


def simple_chunker(wfs, chk_size=DFLT_CHK_SIZE):
    return list(chunker(wfs, chk_size=chk_size))


def simple_featurizer(chks):
    fvs = np.array(list(map(DFLT_FEATURIZER, chks)))
    return fvs


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    step_factories: str = 'step_factories',
    steps: str = 'steps',
    steps_store=None,
    pipelines: str = 'pipelines',
    pipelines_store=None,
    data: str = 'data',
    data_output=None,
    data_store=None,
    learned_models=None,
    models_scores=None,
):
    # TODO: Like to not have this binder logic involving streamlit state here! Contain it!
    if not b.mall():
        # TODO: Maybe it's here that we need to use know.malls.mk_mall?
        b.mall = mall
    mall = b.mall()
    if not b.selected_step_factory():
        b.selected_step_factory = 'chunker'  # TODO make this dynamic

    crudifier = partial(Crudifier, mall=mall)

    steps_store = steps_store or steps
    data_store = data_store or data
    pipelines_store = pipelines_store or pipelines

    @crudifier(
        param_to_mall_map=dict(step_factory=step_factories), output_store=steps_store
    )
    def mk_step(step_factory: Callable, kwargs: dict):
        st.write(f'current value of kwargs={kwargs}')
        kwargs = clean_dict(kwargs)
        step = partial(step_factory, **kwargs)()  # TODO check this
        sig = Sig(step)
        st.write(f'Signature of step made: {sig}')
        return step

    #
    @crudifier(
        # TODO: Want to be able to do this and this only to have the effect
        # param_to_mall_map=dict(steps=steps),
        output_store=pipelines_store,
    )
    def mk_pipeline(steps: Iterable[Callable]):
        # func_steps = (step() for step in steps)
        return LineParametrized(*steps)

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(pipeline=pipelines_store, tagged_data='sound_output'),
        output_store='exec_outputs',
    )
    def exec_pipeline(pipeline: Callable, tagged_data):
        sound, tag = tagged_data
        # if not isinstance(sound, str):
        #     sound = sound.getvalue()

        # arr = sf.read(BytesIO(sound), dtype="int16")[0]
        # result = list(
        #     pipeline(sound)()
        # )  # TODO: because we use FuncFactories we need that hack
        # return result
        result = pipeline(sound)
        return result

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(tagged_data='sound_output'),
        # output_store='exec_outputs'
    )
    def simple_model(tagged_data):
        sound, tag = tagged_data
        if not isinstance(sound, str):
            sound = sound.getvalue()

        arr = sf.read(BytesIO(sound), dtype='int16')[0]

        wfs = np.array(arr)
        st.write(f'wfs = {wfs[:200]}')
        # chks = list(chunker(wfs, chk_size=DFLT_CHK_SIZE))
        # fvs = np.array(list(map(featurizer, chks)))
        # model = Stroll(n_centroids=50)
        # model.fit(X=fvs)
        # scores = model.score_samples(X=fvs)
        # return scores
        return wfs

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(
            tagged_data='sound_output', preprocess_pipeline='pipelines'
        ),
        output_store='learned_models',
    )
    def learn_outlier_model(tagged_data, preprocess_pipeline, n_centroids=50):
        sound, tag = tagged_data
        # if not isinstance(sound, str):
        #     sound = sound.getvalue()

        # arr = sf.read(BytesIO(sound), dtype="int16")[0]

        wfs = np.array(sound)
        st.write(Sig(preprocess_pipeline))
        fvs = preprocess_pipeline(wfs)
        # st.write(f"wfs = {wfs[:200]}")
        # chks = list(chunker(wfs, chk_size=DFLT_CHK_SIZE))
        # fvs = np.array(list(map(featurizer, chks)))
        model = Stroll(n_centroids=50)
        model.fit(X=fvs)
        # scores = model.score_samples(X=fvs)
        # return scores
        return model

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(
            tagged_data='sound_output',
            preprocess_pipeline='pipelines',
            fitted_model='learned_models',
        ),
        output_store='models_scores',
    )
    def apply_fitted_model(tagged_data, preprocess_pipeline, fitted_model):
        sound, tag = tagged_data
        # if not isinstance(sound, str):
        #     sound = sound.getvalue()

        # arr = sf.read(BytesIO(sound), dtype="int16")[0]

        wfs = np.array(sound)
        fvs = preprocess_pipeline(wfs)
        # st.write(f"wfs = {wfs[:200]}")
        # chks = list(chunker(wfs, chk_size=DFLT_CHK_SIZE))
        # fvs = np.array(list(map(featurizer, chks)))
        scores = fitted_model.score_samples(X=fvs)
        # scores = model.score_samples(X=fvs)
        # return scores
        return scores

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(pipeline=pipelines_store),
        # output_store='exec_outputs'
    )
    def visualize_pipeline(pipeline: LineParametrized):
        sig = Sig(pipeline)
        st.write(f'Signature of selected pipeline = {sig}')

        return pipeline

    @crudifier(
        # TODO: Does this work if pipelines_store is a mapping instead of a string?
        param_to_mall_map=dict(scores='models_scores'),
        # output_store='exec_outputs'
    )
    def visualize_scores(scores, threshold=95, num_segs=3):

        intervals_all = scores_to_intervals(scores, threshold, num_segs)
        intervals = [(a, b) for a, b in intervals_all if b > a]

        fig = pyplot_with_intervals(scores, intervals)
        st.pyplot(fig)

        return scores

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: WaveForm, tag: str):
        # mall["tag_store"] = tag
        sound, tag = train_audio, tag
        if not isinstance(sound, bytes):
            sound = sound.getvalue()

        arr = sf.read(BytesIO(sound), dtype='int16')[0]
        return arr, tag

    @crudifier(param_to_mall_map={'result': 'sound_output'})
    def display_tag_sound(result):
        return result

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v == step][0]

    def get_selected_pipeline_sig():
        if not b.selected_pipeline():
            return Sig()
        return Sig(mall[pipelines][b.selected_pipeline()])

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'upload_sound': {
                # NAME_KEY: "Data Loader",
                # "description": {"content": "A very simple learn model example."},
                'execution': {
                    'inputs': {
                        'train_audio': {
                            ELEMENT_KEY: MultiSourceInput,
                            'From a file': {ELEMENT_KEY: FileUploader, 'type': 'wav',},
                            'From the microphone': {ELEMENT_KEY: AudioRecorder},
                        },
                        # "tag": {
                        #     ELEMENT_KEY: TextInput,
                        # },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'Wav loaded successfully.',
                    },
                },
            },
            'display_tag_sound': {
                'execution': {
                    'inputs': {
                        'result': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['sound_output'],
                        },
                    },
                    'output': {ELEMENT_KEY: AudioArrayDisplay,},
                },
            },
            'mk_step': {
                NAME_KEY: 'Pipeline Step Maker',
                'execution': {
                    'inputs': {
                        'step_factory': {'value': b.selected_step_factory,},
                        'kwargs': {
                            'func_sig': Sig(
                                mall[step_factories][b.selected_step_factory()]
                            ),
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
            'mk_pipeline': {
                NAME_KEY: 'Pipeline Maker',
                'execution': {
                    'inputs': {
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': list(mall[steps].values()),
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
            'exec_pipeline': {
                NAME_KEY: 'Pipeline Executor',
                'execution': {
                    'inputs': {
                        'pipeline': {'value': b.selected_pipeline,},
                        'data': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['sound_output'],
                        },
                    }
                },
            },
            'visualize_pipeline': {
                NAME_KEY: 'Pipeline Visualization',
                'execution': {
                    'inputs': {'pipeline': {'value': b.selected_pipeline,},},
                    'output': {
                        ELEMENT_KEY: GraphOutput,
                        NAME_KEY: 'Flow',
                        'use_container_width': True,
                    },
                },
            },
            'visualize_scores': {
                NAME_KEY: 'Scores Visualization',
                'execution': {
                    'inputs': {
                        'scores': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['models_scores'],
                        },
                    },
                    'output': {ELEMENT_KEY: ArrayPlotter,},
                },
            },
            'simple_model': {
                NAME_KEY: 'Learn model',
                'execution': {
                    'inputs': {
                        'tagged_data': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['sound_output'],
                        },
                        'preprocess_pipeline': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['pipelines'],
                        },
                    },
                    'output': {ELEMENT_KEY: ArrayPlotter,},
                },
            },
            'apply_fitted_model': {
                NAME_KEY: 'Apply model',
                'execution': {
                    'inputs': {
                        'tagged_data': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['sound_output'],
                        },
                        'preprocess_pipeline': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['pipelines'],
                        },
                        'learned_model': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['learned_models'],
                        },
                    },
                    'output': {ELEMENT_KEY: ArrayPlotter,},
                },
            },
        },
    }

    funcs = [
        upload_sound,
        display_tag_sound,
        # simple_model,
        # load_data,
        mk_step,
        mk_pipeline,
        learn_outlier_model,
        apply_fitted_model,
        exec_pipeline,
        visualize_pipeline,
        visualize_scores,
    ]
    app = mk_app(funcs, config=config)

    return app


if __name__ == '__main__':

    mall = dict(
        # Factory Input Stores
        sound_output=dict(),
        step_factories=dict(),
        # Output Store
        data=dict(),
        steps=dict(),
        pipelines=dict(),
        exec_outputs=dict(),
        learned_models=dict(),
        models_scores=dict(),
    )

    crudifier = partial(prepare_for_crude_dispatch, mall=mall)

    step_factories = dict(
        # Source Readers
        # data_loader_factory=FuncFactory(data_from_wav_folder),
        # data_loader=data_from_wav_folder,
        # Chunkers
        chunker=FuncFactory(simple_chunker),
        featurizer=FuncFactory(simple_featurizer),
    )

    mall['step_factories'] = step_factories

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories='step_factories', steps='steps', pipelines='pipelines'
    )

    app()
