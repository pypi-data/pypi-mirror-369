import json
import time
from abc import ABC, abstractmethod
from copy import deepcopy
from hashlib import md5
from threading import Lock
from typing import List, Any, Generator, Callable, Tuple, Optional

from duowen_agent.error import LengthLimitExceededError, LLMError
from duowen_agent.llm import OpenAIChat, Message, MessagesSet
from duowen_agent.llm.utils import format_messages
from duowen_agent.utils.core_utils import remove_think, stream_to_string


def continue_chat(
    llm: OpenAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    continue_cnt: int = 3,
    **kwargs,
) -> str:
    full_response = ""  # 存储所有轮次完整响应
    ori_msg = format_messages(messages)
    msg = deepcopy(ori_msg)

    for attempt in range(continue_cnt):
        buffer = ""
        try:
            # 流式获取当前轮次响应
            for chunk in llm.chat_for_stream(msg, **kwargs):
                buffer += chunk

            # 成功完成：累积并返回
            full_response += remove_think(buffer)
            return full_response

        except LengthLimitExceededError as e:
            if attempt == continue_cnt - 1:  # 最后一次尝试仍失败
                # print("-" * 50)
                # print(msg.get_format_messages())
                # print("-" * 50)
                raise e

            # 处理当前部分响应
            current_part = remove_think(buffer)
            full_response += current_part  # 累积到完整响应
            msg = deepcopy(ori_msg)
            # 更新消息历史
            msg.add_assistant(full_response)  # 包含所有历史内容
            msg.add_user("continue")

    return full_response  # 理论上不会执行到这里


def retry_chat(
    llm: OpenAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    stream: bool = True,
    retry_times: int = 3,
    sleep_time: int = 5,
    **kwargs,
) -> str:
    for i in range(retry_times):
        try:
            if stream:
                res = stream_to_string(llm.chat_for_stream(messages, **kwargs))
                return res
            else:
                return llm.chat(messages, **kwargs)
        except LLMError as e:
            if i == retry_times - 1:
                raise e
            else:
                time.sleep(sleep_time)


async def async_continue_chat(
    llm: OpenAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    continue_cnt: int = 3,
    **kwargs,
) -> str:
    full_response = ""  # 存储所有轮次完整响应
    ori_msg = format_messages(messages)
    msg = deepcopy(ori_msg)

    for attempt in range(continue_cnt):
        buffer = ""
        try:
            # 流式获取当前轮次响应
            async for chunk in llm.achat_for_stream(msg, **kwargs):
                buffer += chunk

            # 成功完成：累积并返回
            full_response += remove_think(buffer)
            return full_response

        except LengthLimitExceededError as e:
            if attempt == continue_cnt - 1:  # 最后一次尝试仍失败
                # print("-" * 50)
                # print(msg.get_format_messages())
                # print("-" * 50)
                raise LengthLimitExceededError(content=buffer)

            # 处理当前部分响应
            current_part = remove_think(buffer)
            full_response += current_part  # 累积到完整响应
            msg = deepcopy(ori_msg)
            # 更新消息历史
            msg.add_assistant(full_response)  # 包含所有历史内容
            msg.add_user("continue")

    return full_response


class OpenAIChatBaseCache(ABC):

    def __init__(
        self,
        llm: OpenAIChat,
        ttl: Optional[int] = 3600,
        lock: Optional[Lock] = None,
        observation_func: Optional[
            Callable[[str], Tuple[bool, Any]]
        ] = None,  # 只有chat接口存在观测检查
    ) -> None:
        self.llm = llm
        self.ttl = ttl
        self.lock = lock or Lock()
        self.observation_func = observation_func
        self.params = [
            "temperature",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "max_tokens",
            "stop",
        ]

    def chat(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        **kwargs,
    ) -> str | Any:
        """
        messages: 消息历史
        observation_func: 自定义观察函数 input:模型返回结果, output:观察状态，观察结果
        """
        messages = format_messages(messages)
        _key = self._compute_key(messages, **kwargs)
        _res_cache = self.get(_key)

        if _res_cache:
            if self.observation_func:
                _observation_status, _observation_res = self.observation_func(
                    _res_cache
                )
                if _observation_status:
                    return _observation_res
                else:
                    self.delete(_key)
                    return _observation_res
            else:
                return _res_cache

        _resp = stream_to_string(self.llm.chat_for_stream(messages, **kwargs))

        if self.observation_func:
            _observation_status, _observation_res = self.observation_func(_resp)
            if _observation_status:
                self.upsert(_key, messages, _resp, **kwargs)
                return _observation_res
            else:
                return _observation_res
        else:
            self.upsert(_key, messages, _resp)
            return _resp

    def chat_for_stream(
        self, messages: str | List[dict] | List[Message] | MessagesSet, **kwargs
    ) -> Generator:
        messages = format_messages(messages)
        _key = self._compute_key(messages, **kwargs)
        _res = self.get(_key)
        if _res:
            chunk_size = 4
            for i in range(0, len(_res), chunk_size):
                yield _res[i : i + chunk_size]
            return

        _buffer = ""
        for chunk in self.llm.chat_for_stream(messages, **kwargs):
            _buffer += chunk
            yield chunk
        self.upsert(_key, messages, _buffer, **kwargs)
        return

    def _compute_key(self, messages: MessagesSet, **kwargs):
        param_str = json.dumps(
            {k: v for k, v in kwargs.items() if k in self.params},
            sort_keys=True,
            ensure_ascii=False,
        )
        return md5(
            (messages.get_format_messages() + self.llm.model + param_str).encode()
        ).hexdigest()

    def get(self, key: str):
        with self.lock:
            _res = self._get(key)
            if _res:
                _data = json.loads(_res)
                if _data["expire"] is None or _data["expire"] > time.time():
                    return _data["return"]
                else:
                    self._delete(key)
                    return None
            else:
                return None

    def upsert(self, key: str, prompt: MessagesSet, value: str, **kwargs):
        with self.lock:
            param_str = {k: v for k, v in kwargs.items() if k in self.params}
            return self._upsert(
                key,
                json.dumps(
                    {
                        "input": prompt.model_dump()["message_list"],
                        "return": value,
                        "model": self.llm.model,
                        "expire": int(time.time()) + self.ttl if self.ttl else None,
                        **param_str,
                    },
                    ensure_ascii=False,
                ),
            )

    def delete(self, key: str):
        with self.lock:
            if self._exists(key):
                return self._delete(key)

    @abstractmethod
    def _get(self, key: str) -> str | None:
        """
        子类实现不应再获取锁
        return: json.dumps({"input": str, "return": str, "model": str, "expire": int or null}
        """
        raise NotImplementedError

    @abstractmethod
    def _upsert(self, key: str, value: str) -> bool:
        """
        子类实现不应再获取锁
        value: json.dumps({"input": str, "return": str, "model": str, "expire": int or null}
        接口可以自行扩展
        """
        raise NotImplementedError

    @abstractmethod
    def _delete(self, key: str) -> bool:
        """
        子类实现不应再获取锁
        """
        raise NotImplementedError

    @abstractmethod
    def _exists(self, key: str) -> bool:
        """
        子类实现不应再获取锁
        """
        raise NotImplementedError
