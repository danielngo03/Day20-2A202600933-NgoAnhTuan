# Design Template

## Problem

Xây dựng một hệ thống nghiên cứu đa tác vụ (multi-agent) tự động nhận một câu hỏi mở, tìm kiếm thông tin, tổng hợp, và trình bày lại kết quả dưới dạng câu trả lời chi tiết và logic. Hệ thống cần kết nối với OpenRouter để gọi mô hình ngôn ngữ và sử dụng Wikipedia để lấy ngữ cảnh.

## Why multi-agent?

Mô hình single-agent không đủ vì:
- Agent phải gánh vác quá nhiều tác vụ cùng một lúc (tìm kiếm, trích xuất, lập luận, viết văn), dẫn đến prompt quá tải và dễ bị hallucination.
- Không có cơ chế tự kiểm duyệt (self-reflection) chuyên sâu.
- Khó chia nhỏ bài toán để debug hoặc mở rộng. Trong multi-agent, chúng ta tách biệt các vai trò để LLM dễ dàng "focus" vào từng task cụ thể.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối các agent, kiểm tra điều kiện dừng. | `ResearchState` hiện tại | Lựa chọn agent tiếp theo hoặc END | `max_iterations` bị vượt qua do lặp vô hạn. |
| Researcher | Tìm kiếm trên Wikipedia, tổng hợp nguồn. | Query, Route history | `state.sources`, `state.research_notes` | Không tìm thấy nguồn thông tin, hoặc lỗi mạng. |
| Analyst | Phân tích thông tin từ Researcher. | `state.research_notes` | `state.analysis_notes` | Thông tin đầu vào quá rời rạc, khó tổng hợp. |
| Writer | Viết câu trả lời cuối cùng. | `state.analysis_notes` | `state.final_answer` | Trả lời không đúng trọng tâm. |
| Critic | Đánh giá và kiểm duyệt câu trả lời. | `state.final_answer` | Critique notes | Đánh giá quá khắt khe hoặc bỏ sót lỗi sai. |

## Shared state

- `request` (ResearchQuery): Lưu query ban đầu từ user.
- `iteration` (int): Dùng làm guardrail chống lặp vô hạn.
- `route_history` (list[str]): Trace luồng đi của hệ thống.
- `sources` (list[SourceDocument]): Danh sách tài liệu thô.
- `research_notes` (str): Ghi chú tóm tắt từ Researcher.
- `analysis_notes` (str): Các phân tích logic từ Analyst.
- `final_answer` (str): Câu trả lời cuối từ Writer kèm theo critique.
- `errors` (list[str]): Ghi lại lỗi nếu có fallback xảy ra.

## Routing policy

Graph sử dụng LangGraph với kiến trúc dạng vòng (hub-and-spoke):
Tất cả các worker (Researcher, Analyst, Writer, Critic) đều trả kết quả về cho Supervisor. Supervisor quyết định bước tiếp theo:
1. Nếu chưa có `research_notes` -> gọi Researcher
2. Nếu chưa có `analysis_notes` -> gọi Analyst
3. Nếu chưa có `final_answer` -> gọi Writer
4. Nếu có `final_answer` nhưng chưa được review -> gọi Critic
5. Nếu đã được review -> trả về END.

## Guardrails

- Max iterations: Cấu hình trong `.env` (mặc định 6). Nếu quá số lần sẽ force END.
- Timeout: Cấu hình trong `.env`.
- Retry: Có try-catch fallback ở Supervisor nếu gọi LLM hoặc parse JSON lỗi.
- Validation: Các state đều được validate bằng Pydantic models.

## Benchmark plan

- Query: "Nghiên cứu về GraphRAG state-of-the-art"
- Metric: Latency (thời gian chạy), Token Cost, Quality Score, Citation coverage.
- Expected outcome: Multi-agent chạy chậm hơn và tốn token hơn nhưng đưa ra câu trả lời chi tiết, có cấu trúc chặt chẽ và ít hallucination hơn hẳn Single-agent.
