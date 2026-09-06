#!/bin/bash
# decode-all.sh - 文件夹和文件一同显示，数字编号选择

echo "========================================"
echo "  Base64 文件名解码工具"
echo "========================================"
echo ""
echo "当前目录: $(pwd)"
echo ""

# 扫描文件夹和文件
items=()
types=()
i=1

# 先显示文件夹
for d in */; do
    if [ -d "$d" ]; then
        name="${d%/}"
        echo "  [$i] 📁 $name/"
        items+=("$name")
        types+=("folder")
        i=$((i + 1))
    fi
done

# 再显示文件
for f in *; do
    if [ -f "$f" ]; then
        name=$(basename "$f")
        if [ ${#name} -gt 50 ]; then
            name="${name:0:47}..."
        fi
        echo "  [$i] 📄 $name"
        items+=("$f")
        types+=("file")
        i=$((i + 1))
    fi
done

if [ ${#items[@]} -eq 0 ]; then
    echo "  (该目录为空)"
    echo ""
    echo "输入新目录路径 (如 /c/Users/Downloads):"
    read -p "> " new_dir
    if [ -d "$new_dir" ]; then
        cd "$new_dir"
        exec bash "$0"
    else
        echo "目录不存在"
        exit 1
    fi
fi

echo ""
echo "选择方式："
echo "  - 数字: 3 (进入文件夹 或 解码文件)"
echo "  - 范围: 3-7"
echo "  - 多个: 2,4,6 (仅限文件)"
echo "  - 全部: all (仅限文件)"
echo "  - 切换目录: cd"
echo "  - 退出: q"
echo ""
read -p "请选择: " choice

case "$choice" in
    q|Q)
        echo "退出"
        exit 0
        ;;
    cd|CD)
        echo ""
        read -p "输入目录路径: " new_dir
        if [ -d "$new_dir" ]; then
            cd "$new_dir"
            exec bash "$0"
        else
            echo "目录不存在"
            exit 1
        fi
        ;;
    all)
        # 只选择文件，不选文件夹
        selected=()
        for ((idx=0; idx<${#items[@]}; idx++)); do
            if [ "${types[$idx]}" = "file" ]; then
                selected+=("${items[$idx]}")
            fi
        done
        ;;
    *)
        selected=()
        # 解析输入，支持数字、范围、多个
        if [[ "$choice" =~ ^[0-9]+$ ]]; then
            idx=$((choice - 1))
            if [ $idx -ge 0 ] && [ $idx -lt ${#items[@]} ]; then
                # 判断是文件夹还是文件
                if [ "${types[$idx]}" = "folder" ]; then
                    cd "${items[$idx]}"
                    exec bash "$0"
                else
                    selected+=("${items[$idx]}")
                fi
            else
                echo "编号 $choice 无效"
                exit 1
            fi
        elif [[ "$choice" =~ ^[0-9]+-[0-9]+$ ]]; then
            start=$(echo "$choice" | cut -d'-' -f1)
            end=$(echo "$choice" | cut -d'-' -f2)
            for ((i=start; i<=end; i++)); do
                idx=$((i - 1))
                if [ $idx -ge 0 ] && [ $idx -lt ${#items[@]} ] && [ "${types[$idx]}" = "file" ]; then
                    selected+=("${items[$idx]}")
                fi
            done
        elif [[ "$choice" =~ ^[0-9,]+$ ]]; then
            IFS=',' read -r -a nums <<< "$choice"
            for num in "${nums[@]}"; do
                idx=$((num - 1))
                if [ $idx -ge 0 ] && [ $idx -lt ${#items[@]} ] && [ "${types[$idx]}" = "file" ]; then
                    selected+=("${items[$idx]}")
                fi
            done
        else
            echo "无法识别: $choice"
            exit 1
        fi
        ;;
esac

if [ ${#selected[@]} -eq 0 ]; then
    echo "没有选择任何文件"
    exit 1
fi

echo ""
echo "将处理 ${#selected[@]} 个文件..."
echo ""

success=0
failed=0
count=0

for file in "${selected[@]}"; do
    count=$((count + 1))
    echo -n "[$count] $file ... "

    base="${file%.*}"
    ext="${file##*.}"
    [ "$base" = "$file" ] && ext="" && encoded="$file" || encoded="$base"

    b64="${encoded//-/+}"
    b64="${b64//_//}"
    mod=$(( ${#b64} % 4 ))
    if [ $mod -ne 0 ]; then
        for ((i=0; i<4-mod; i++)); do
            b64="${b64}="
        done
    fi

    decoded=$(echo "$b64" | base64 -d 2>/dev/null)
    if [ -z "$decoded" ] || [ "$decoded" = "$encoded" ]; then
        echo "跳过 (无法解码)"
        continue
    fi

    [ -n "$ext" ] && newname="${decoded}.${ext}" || newname="$decoded"

    if [ -e "$newname" ]; then
        suffix=1
        while [ -e "${newname%.*}_${suffix}.${ext}" ] || [ -e "${newname}_${suffix}" ]; do
            suffix=$((suffix + 1))
        done
        [ -n "$ext" ] && newname="${newname%.*}_${suffix}.${ext}" || newname="${newname}_${suffix}"
    fi

    if mv "$file" "$newname" 2>/dev/null; then
        echo "✓ $newname"
        success=$((success + 1))
    else
        echo "✗ 失败"
        failed=$((failed + 1))
    fi
done

echo ""
echo "完成！成功: $success, 失败: $failed"