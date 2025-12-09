from datetime import datetime
import csv
import statistics
import sys

# زيادة حد العودية (احتياطياً)
sys.setrecursionlimit(5000)
# ==========================================
# Pure Helper Functions (Recursive)
# ==========================================

def parse_date(date_str):
    """
    تحاول تنسيق التاريخ باستخدام العودية بدلاً من حلقة for.
    Concept: Recursion over list of formats.
    """
    if date_str is None or date_str == "":
        return "UNKNOWN"

    # قائمة الصيغ المتاحة
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]

    # دالة داخلية عودية لتجربة الصيغ
    def try_parse_recursive(fmt_list):
        # Base Case: انتهت الصيغ ولم ننجح
        if not fmt_list:
            return date_str

        # Recursive Step: جرب الرأس (Head)، وإذا فشل جرب الذيل (Tail)
        current_fmt, *remaining_fmts = fmt_list
        try:
            dt = datetime.strptime(date_str.strip(), current_fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return try_parse_recursive(remaining_fmts)

    return try_parse_recursive(formats)


def safe_float(value, default=0.0):
    # هذه الدالة بسيطة ولا تحتاج تعديل لأنها لا تحتوي على loops
    try:
        return float(value)
    except Exception:
        return default


def stats_summary(values):
    """
    حساب الإحصائيات.
    تم استبدال List Comprehension بأسلوب عودي لتنظيف البيانات.
    """

    # دالة عودية لتصفية القيم None (بديل لـ List Comprehension)
    def recursive_clean(lst, acc=None):
        if acc is None:
            acc = []
        if not lst:
            return acc

        head, *tail = lst
        if head is not None:
            new_acc = acc + [head]
        else:
            new_acc = acc
        return recursive_clean(tail, new_acc)

    # 1. تنظيف البيانات عودياً
    clean_values = recursive_clean(values)

    if not clean_values:
        return {"count": 0}

    # ملاحظة: دوال statistics هي دوال جاهزة وتعتبر "black box".
    # في البرمجة الوظيفية، استخدام دوال المكتبات مقبول طالما لا تغير الحالة (Pure).
    return {
        "count": len(clean_values),
        "mean": statistics.mean(clean_values),
        "median": statistics.median(clean_values),
        "variance": statistics.pvariance(clean_values) if len(clean_values) > 1 else 0.0,
        "min": min(clean_values),
        "max": max(clean_values)
    }


# ==========================================
# I/O Operations (Impure but Recursive Control Flow)
# ==========================================

def write_csv(path, fieldnames, rows):
    """
    كتابة ملف CSV.
    على الرغم من أنها Impure، سنستخدم العودية للتحكم في التكرار بدلاً من for loop.
    تطبيقاً لمبدأ: Functional programs do not contain loops [Section 2].
    """
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # دالة عودية للكتابة صف بصف
        # [Concept: Tail Recursion replacing Loop]
        def write_rows_recursive(row_list):
            if not row_list:
                return

            head, *tail = row_list
            writer.writerow(head)  # Side Effect
            write_rows_recursive(tail)

        write_rows_recursive(rows)