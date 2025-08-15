"""
NextStop Agent.

Run queries using the NextStop Agent.
"""
from collections.abc import Callable
import asyncio
from pathlib import Path
from pandas import DataFrame
from navconfig import BASE_DIR
# Parrot Tools:
from parrot.tools.weather import OpenWeather
from parrot.tools import PythonREPLTool
from parrot.tools.excel import ExcelTool
from parrot.tools.gvoice import GoogleVoiceTool
from parrot.tools.pdf import PDFPrintTool
# Inherited interfaces:
from ..interfaces.parrot import AgentBase
# Tools:
from ..interfaces.parrot.tools import (
    StoreInfo,
)
from .flow import FlowComponent


class NextStopAgent(AgentBase, FlowComponent):
    """NextStopAgent.

    Overview:
        The NextStopAgent class is a FlowComponent that integrates with the Parrot AI Agent framework to run queries
        using the NextStop Agent. It extends the AgentBase class and provides methods for creating and managing the
        agent's lifecycle within a FlowTask.

    """
    _agent_name: str = 'NextStopAgent'
    agent_id: str = 'nextstop_agent'

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    def _define_tools(self, base_dir: Path):
        return [
            OpenWeather(request='weather'),
            PythonREPLTool(
                report_dir=base_dir.joinpath(self._agent_name, 'documents')
            ),
            GoogleVoiceTool(
                output_dir=base_dir.joinpath(self._agent_name, 'podcasts')
            ),
            PDFPrintTool(
                output_dir=base_dir.joinpath(self._agent_name, 'documents', 'pdf')
            ),
            ExcelTool(
                output_dir=base_dir.joinpath(self._agent_name, 'documents', 'excel')
            ),
        ] + StoreInfo().get_tools()

    async def start(self, **kwargs):
        """
        start.

            Initialize (if needed) a task
        """
        if self.previous:
            self.data = self.input

        # check if previous data is an iterable:
        if isinstance(self.data, DataFrame):
            self._iterable = self.data.iterrows()
        await super().start(**kwargs)

    async def close(self):
        pass

    async def run(self):
        if hasattr(self, 'query'):
            self.user_id = 35
            # Do an arbitrary query to ask_agent:
            self.logger.info(f"Running query: {self.query}")
            response, answer = await self.ask_agent(
                userid=self.user_id,
                query=self.query
            )
        elif hasattr(self, 'type'):
            query = await self.open_prompt(self.type)
            question = query.format(
                employee_id='khill@hisenseretail.com'
            )
            user_id = '496'
            response, answer = await self.ask_agent(
                userid=user_id,
                query=question
            )
            # Then, generate files based on the response:
            response, answer = await self.generate_files(
                response=answer,
                userid=user_id
            )
            print('RESPONSE:', response)
        return True
