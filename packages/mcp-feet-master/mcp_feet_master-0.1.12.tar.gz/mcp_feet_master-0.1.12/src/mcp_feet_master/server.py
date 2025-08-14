"""MCP feet Master Server Implementation."""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 導入 mineru OCR 功能
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
mineru_file = os.path.join(current_dir, "mineru_ocr.py")
OCR_MISSING_DEPS = []

if os.path.exists(mineru_file):
    try:
        from .mineru_ocr import parse_single_file
        OCR_AVAILABLE = True
    except ImportError as e:
        OCR_AVAILABLE = False
        # 解析具體缺失的依賴項
        error_msg = str(e)
        if "loguru" in error_msg:
            OCR_MISSING_DEPS.append("loguru")
        if "mineru" in error_msg:
            OCR_MISSING_DEPS.append("mineru")
        if not OCR_MISSING_DEPS:
            OCR_MISSING_DEPS.append("unknown dependencies")
else:
    OCR_AVAILABLE = False
    OCR_MISSING_DEPS.append("mineru_ocr.py file")

# 導入 VCP 控制功能
try:
    from .monitor_vcp_code_setting import vcp_setting_tool, _iter_physical_monitors, test_camera_vcp_support
    VCP_AVAILABLE = True
except ImportError:
    VCP_AVAILABLE = False


def create_server() -> FastMCP:
    """Create and configure the MCP feet Master server."""
    
    # Create FastMCP server instance
    mcp = FastMCP("MCP feet Master")

    @mcp.tool()
    def get_foot_num(rabbits: int, chickens: int) -> dict:
        """
        Calculate the total number of feet for rabbits and chickens.
        
        Rabbits have 4 feet, chickens have 2 feet.
        
        Args:
            rabbits: Number of rabbits
            chickens: Number of chickens
            
        Returns:
            Dictionary containing calculation results, including:
            - total_feet: Total number of feet
            - rabbit_feet: Total feet from rabbits
            - chicken_feet: Total feet from chickens
            - calculation: Calculation process description
        """
        # Input validation
        if rabbits < 0:
            raise ValueError("Number of rabbits cannot be negative")
        if chickens < 0:
            raise ValueError("Number of chickens cannot be negative")
        
        # Calculate
        rabbit_feet = rabbits * 4
        chicken_feet = chickens * 2
        total_feet = rabbit_feet + chicken_feet
        
        return {
            "total_feet": total_feet,
            "rabbit_feet": rabbit_feet,
            "chicken_feet": chicken_feet,
            "rabbits": rabbits,
            "chickens": chickens,
            "calculation": f"{rabbits} rabbits x 4 feet + {chickens} chickens x 2 feet = {total_feet} feet",
            "formula": f"{rabbits} x 4 + {chickens} x 2 = {total_feet}"
        }

    @mcp.tool()
    def calculate_animals_from_feet(total_feet: int, animal_type: str = "mixed") -> dict:
        """
        Calculate animal count from total feet (bonus feature).
        
        Args:
            total_feet: Total number of feet
            animal_type: Animal type ("rabbits", "chickens", "mixed")
            
        Returns:
            Possible animal combinations
        """
        if total_feet < 0:
            raise ValueError("Total feet cannot be negative")
        
        if animal_type == "rabbits":
            if total_feet % 4 == 0:
                return {
                    "possible": True,
                    "rabbits": total_feet // 4,
                    "chickens": 0,
                    "explanation": f"{total_feet} feet can be {total_feet // 4} rabbits"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} feet cannot be made with only rabbits (rabbits have 4 feet)"
                }
        
        elif animal_type == "chickens":
            if total_feet % 2 == 0:
                return {
                    "possible": True,
                    "rabbits": 0,
                    "chickens": total_feet // 2,
                    "explanation": f"{total_feet} feet can be {total_feet // 2} chickens"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} feet cannot be made with only chickens (chickens have 2 feet)"
                }
        
        else:  # mixed
            combinations = []
            for rabbits in range(total_feet // 4 + 1):
                remaining_feet = total_feet - (rabbits * 4)
                if remaining_feet % 2 == 0:
                    chickens = remaining_feet // 2
                    combinations.append({
                        "rabbits": rabbits,
                        "chickens": chickens,
                        "verification": rabbits * 4 + chickens * 2
                    })
            
            return {
                "total_feet": total_feet,
                "possible_combinations": combinations,
                "count": len(combinations)
            }

    @mcp.tool()
    def process_image_edge(input_path: str, output_path: str = None) -> dict:
        """
        Process image to detect edges and save the result.
        
        Args:
            input_path: Path to input image (.jpg or .png)
            output_path: Path to save edge result (optional, defaults to input_path_edge.jpg)
            
        Returns:
            Dictionary containing processing results
        """
        # Input validation
        if not os.path.exists(input_path):
            raise ValueError(f"Input file does not exist: {input_path}")
        
        if not input_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValueError("Only .jpg, .jpeg, and .png files are supported")
        
        # Generate output path if not provided
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_edge.jpg"
        
        try:
            # Read image
            image = cv2.imread(input_path)
            if image is None:
                raise ValueError(f"Cannot read image: {input_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 100, 200)
            
            # Save result
            cv2.imwrite(output_path, edges)
            
            return {
                "status": "success",
                "input_path": input_path,
                "output_path": output_path,
                "input_size": f"{image.shape[1]}x{image.shape[0]}",
                "processing": "Canny edge detection applied",
                "message": f"Edge detection completed and saved to {output_path}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "input_path": input_path,
                "error": str(e)
            }

    @mcp.tool()
    def check_camera_monitor() -> dict:
        """
        Check if there are external monitors that support camera VCP controls.
        Actually tests VCP code 233 to verify camera control capability.
        
        Returns:
            Dictionary containing detection results
        """
        if not VCP_AVAILABLE:
            return {
                "status": "error",
                "message": "VCP control not available",
                "monitors_found": 0,
                "camera_capable": False,
                "camera_monitors": []
            }
        
        try:
            # 獲取所有螢幕但不自動關閉 handle
            handles = []
            def collect_handles():
                temp_handles = []
                for handle in _iter_physical_monitors(close_handles=False):
                    temp_handles.append(handle)
                return temp_handles
            
            handles = collect_handles()
            monitor_count = len(handles)
            camera_monitors = []
            
            # 測試每個螢幕是否支援相機 VCP 控制
            for i, handle in enumerate(handles):
                if i > 0:  # 跳過第一個（通常是主螢幕）
                    try:
                        if test_camera_vcp_support(handle):
                            camera_monitors.append({
                                "monitor_index": i,
                                "camera_capable": True,
                                "message": f"Monitor {i} supports camera VCP controls"
                            })
                        else:
                            camera_monitors.append({
                                "monitor_index": i,
                                "camera_capable": False,
                                "message": f"Monitor {i} does not support camera VCP controls"
                            })
                    except Exception as e:
                        camera_monitors.append({
                            "monitor_index": i,
                            "camera_capable": False,
                            "message": f"Monitor {i} test failed: {str(e)}"
                        })
                else:
                    # 也記錄主螢幕的狀態
                    camera_monitors.append({
                        "monitor_index": i,
                        "camera_capable": False,
                        "message": f"Monitor {i} (main monitor) - camera control not tested"
                    })
            
            # 檢查是否有任何螢幕支援相機控制
            camera_capable = any(m["camera_capable"] for m in camera_monitors)
            
            return {
                "status": "success",
                "monitors_found": monitor_count,
                "camera_capable": camera_capable,
                "camera_monitors": camera_monitors,
                "message": f"Found {monitor_count} monitors, {len([m for m in camera_monitors if m['camera_capable']])} support camera controls"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Detection failed: {str(e)}",
                "monitors_found": 0,
                "camera_capable": False,
                "camera_monitors": []
            }

    @mcp.tool()
    def camera_blur_control(enable: bool) -> dict:
        """
        Control camera background blur on/off.
        
        Args:
            enable: True to enable blur, False to disable blur
            
        Returns:
            Dictionary containing operation results
        """
        if not VCP_AVAILABLE:
            return {
                "status": "error",
                "message": "VCP control not available"
            }
        
        try:
            if enable:
                result = vcp_setting_tool(233, 11521)  # Enable blur
                action = "enabled"
            else:
                result = vcp_setting_tool(233, 11520)  # Disable blur
                action = "disabled"
            
            return {
                "status": "success",
                "action": f"Background blur {action}",
                "message": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Camera blur control failed: {str(e)}"
            }

    @mcp.tool()
    def camera_autoframing_control(enable: bool) -> dict:
        """
        Control camera auto framing on/off.
        
        Args:
            enable: True to enable auto framing, False to disable auto framing
            
        Returns:
            Dictionary containing operation results
        """
        if not VCP_AVAILABLE:
            return {
                "status": "error",
                "message": "VCP control not available"
            }
        
        try:
            if enable:
                result = vcp_setting_tool(233, 11265)  # Enable auto framing
                action = "enabled"
            else:
                result = vcp_setting_tool(233, 11264)  # Disable auto framing
                action = "disabled"
            
            return {
                "status": "success",
                "action": f"Auto framing {action}",
                "message": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Camera auto framing control failed: {str(e)}"
            }

    # @mcp.tool()
    # def check_md_exists(file_path: str) -> dict:
    #     """
    #     Check if a corresponding .md file exists for the given document file.
        
    #     Args:
    #         file_path: Path to the document file (PDF, PNG, JPG, etc.)
            
    #     Returns:
    #         Dictionary containing check results
    #     """
    #     try:
    #         # Convert to Path object
    #         input_path = Path(file_path)
            
    #         # Check if input file exists
    #         if not input_path.exists():
    #             return {
    #                 "status": "error",
    #                 "message": f"Input file does not exist: {file_path}",
    #                 "md_exists": False,
    #                 "md_path": None
    #             }
            
    #         # Generate expected .md file path (same directory, same name with .md extension)
    #         md_path = input_path.parent / f"{input_path.stem}.md"
            
    #         # Check if .md file exists
    #         md_exists = md_path.exists()
            
    #         return {
    #             "status": "success",
    #             "input_file": str(input_path),
    #             "md_path": str(md_path),
    #             "md_exists": md_exists,
    #             "message": f"MD file {'exists' if md_exists else 'does not exist'} at {md_path}"
    #         }
            
    #     except Exception as e:
    #         return {
    #             "status": "error",
    #             "message": f"Check MD file failed: {str(e)}",
    #             "md_exists": False,
    #             "md_path": None
    #         }

    # @mcp.tool()
    # def process_document_ocr(file_path: str, language: str = "en") -> dict:
    #     """
    #     Process document using OCR and save result as .md file in the same directory.
    #     Simply calls parse_single_file function.
        
    #     Args:
    #         file_path: Path to the document file (PDF, PNG, JPG, etc.)
    #         language: Language for OCR processing (default: "en")
            
    #     Returns:
    #         Dictionary containing processing results
    #     """
    #     if not OCR_AVAILABLE:
    #         if OCR_MISSING_DEPS:
    #             missing_items = ", ".join(OCR_MISSING_DEPS)
    #             return {
    #                 "status": "error",
    #                 "message": f"OCR functionality not available. Missing: {missing_items}. Please install required dependencies: pip install loguru mineru"
    #             }
    #         else:
    #             return {
    #                 "status": "error",
    #                 "message": "OCR functionality not available. Unknown error occurred during import."
    #             }
        
    #     try:
    #         # Convert to Path object for validation
    #         input_path = Path(file_path)
            
    #         # Check if input file exists
    #         if not input_path.exists():
    #             return {
    #                 "status": "error",
    #                 "message": f"Input file does not exist: {file_path}"
    #             }
            
    #         # Check supported file types
    #         supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    #         if input_path.suffix.lower() not in supported_extensions:
    #             return {
    #                 "status": "error",
    #                 "message": f"Unsupported file type. Supported: {supported_extensions}"
    #             }
            
    #         # Prepare output directory (same as input file directory)
    #         output_dir = str(input_path.parent)
            
    #         # Simply call parse_single_file function
    #         parse_single_file(
    #             path=str(input_path),
    #             output_dir=output_dir,
    #             lang=language,
    #             backend="pipeline",
    #             method="auto"
    #         )
            
    #         # Check if output file was created
    #         # OCR creates files in xxxx/auto/xxxx.md structure
    #         md_path = input_path.parent / input_path.stem / "auto" / f"{input_path.stem}.md"
            
    #         if md_path.exists():
    #             return {
    #                 "status": "success",
    #                 "input_file": str(input_path),
    #                 "output_file": str(md_path),
    #                 "language": language,
    #                 "message": f"OCR processing completed successfully. Output saved to {md_path}"
    #             }
    #         else:
    #             return {
    #                 "status": "error",
    #                 "message": f"OCR processing completed but output file not found at {md_path}",
    #                 "input_file": file_path
    #             }
            
    #     except Exception as e:
    #         return {
    #             "status": "error",
    #             "message": f"OCR processing failed: {str(e)}",
    #             "input_file": file_path
    #         }

    # @mcp.tool()
    # def read_md_content(file_path: str) -> dict:
    #     """
    #     Read the content of a .md file. If file_path is not .md, 
    #     it will look for corresponding .md file in the same directory.
        
    #     Args:
    #         file_path: Path to the .md file or original document file
            
    #     Returns:
    #         Dictionary containing file content
    #     """
    #     try:
    #         input_path = Path(file_path)
            
    #         # If input is not .md file, look for corresponding .md file
    #         if input_path.suffix.lower() != '.md':
    #             # Look for .md file in xxxx/auto/xxxx.md structure
    #             md_path = input_path.parent / input_path.stem / "auto" / f"{input_path.stem}.md"
    #         else:
    #             md_path = input_path
            
    #         # Check if .md file exists
    #         if not md_path.exists():
    #             return {
    #                 "status": "error",
    #                 "message": f"MD file does not exist: {md_path}",
    #                 "content": None
    #             }
            
    #         # Read file content
    #         with open(md_path, 'r', encoding='utf-8') as f:
    #             content = f.read()
            
    #         return {
    #             "status": "success",
    #             "md_file": str(md_path),
    #             "content": content,
    #             "content_length": len(content),
    #             "message": f"Successfully read {len(content)} characters from {md_path}"
    #         }
            
    #     except Exception as e:
    #         return {
    #             "status": "error",
    #             "message": f"Read MD file failed: {str(e)}",
    #             "content": None
    #         }

    return mcp

def main() -> None:
    """Main entry point for running the server."""
    try:
        server = create_server()
        print("MCP feet Master Server starting...")
        print("Available tools:")
        print("   - get_foot_num(rabbits, chickens): Calculate total feet")
        print("   - calculate_animals_from_feet(total_feet, animal_type): Calculate animals from feet")
        print("   - process_image_edge(input_path, output_path): Process image edge detection")
        print("   - check_camera_monitor(): Check for camera-capable monitors")
        print("   - camera_blur_control(enable): Control camera background blur")
        print("   - camera_autoframing_control(enable): Control camera auto framing")
        print("   - check_md_exists(file_path): Check if MD file exists for document")
        print("   - process_document_ocr(file_path, language): Process document with OCR")
        print("   - read_md_content(file_path): Read content from MD file")
        print()
        print("Server ready to accept connections!")
        
        # Run server
        server.run()
        
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()