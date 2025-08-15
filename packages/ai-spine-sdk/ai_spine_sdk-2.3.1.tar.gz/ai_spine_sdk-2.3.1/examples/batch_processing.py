"""Batch processing example for AI Spine SDK."""

import time
import concurrent.futures
from typing import List, Dict, Any, Tuple
from ai_spine import Client, AISpineError, InsufficientCreditsError


def process_single_item(
    client: Client,
    flow_id: str,
    item: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """Process a single item through a flow.
    
    Args:
        client: AI Spine client
        flow_id: Flow to execute
        item: Input data item
        
    Returns:
        Tuple of (item_id, result)
    """
    item_id = item.get("id", "unknown")
    
    try:
        # Execute and wait for completion
        result = client.execute_and_wait(
            flow_id=flow_id,
            input_data=item,
            timeout=120  # 2 minutes per item
        )
        
        return item_id, {
            "status": "success",
            "output": result.get("output_data"),
            "execution_id": result.get("execution_id")
        }
    
    except InsufficientCreditsError as e:
        return item_id, {
            "status": "error",
            "error": f"Insufficient credits: {e}",
            "error_type": "insufficient_credits"
        }
    except AISpineError as e:
        return item_id, {
            "status": "error",
            "error": str(e),
            "error_type": "general"
        }


def batch_process_sequential(
    client: Client,
    flow_id: str,
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Process items sequentially.
    
    Args:
        client: AI Spine client
        flow_id: Flow to execute
        items: List of input items
        
    Returns:
        Processing results
    """
    results = {}
    start_time = time.time()
    
    for i, item in enumerate(items, 1):
        print(f"Processing item {i}/{len(items)}...")
        item_id, result = process_single_item(client, flow_id, item)
        results[item_id] = result
        
        # Add small delay to avoid rate limiting
        if i < len(items):
            time.sleep(0.5)
    
    elapsed = time.time() - start_time
    
    return {
        "results": results,
        "total_items": len(items),
        "successful": sum(1 for r in results.values() if r["status"] == "success"),
        "failed": sum(1 for r in results.values() if r["status"] == "error"),
        "elapsed_time": elapsed
    }


def batch_process_parallel(
    client: Client,
    flow_id: str,
    items: List[Dict[str, Any]],
    max_workers: int = 3
) -> Dict[str, Any]:
    """Process items in parallel.
    
    Args:
        client: AI Spine client
        flow_id: Flow to execute
        items: List of input items
        max_workers: Maximum parallel workers
        
    Returns:
        Processing results
    """
    results = {}
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {
            executor.submit(process_single_item, client, flow_id, item): item
            for item in items
        }
        
        # Collect results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(future_to_item), 1):
            item = future_to_item[future]
            item_id = item.get("id", "unknown")
            
            try:
                _, result = future.result()
                results[item_id] = result
                print(f"Completed {i}/{len(items)}: {item_id}")
            except Exception as e:
                results[item_id] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"Failed {i}/{len(items)}: {item_id} - {e}")
    
    elapsed = time.time() - start_time
    
    return {
        "results": results,
        "total_items": len(items),
        "successful": sum(1 for r in results.values() if r["status"] == "success"),
        "failed": sum(1 for r in results.values() if r["status"] == "error"),
        "elapsed_time": elapsed
    }


def main():
    # Initialize client with API key
    client = Client(api_key="sk_your_api_key_here")
    
    # Check credits before processing batch
    try:
        credits = client.check_credits()
        print(f"Available credits: {credits}")
        
        # Estimate required credits (assuming 1 credit per item)
        estimated_credits = 5  # We have 5 items in the batch
        
        if credits < estimated_credits:
            print(f"Warning: You may not have enough credits for all items.")
            print(f"Required: ~{estimated_credits}, Available: {credits}")
            print("Consider topping up at https://ai-spine.com/billing")
    except Exception as e:
        print(f"Could not check credits: {e}")
    
    # Prepare batch data
    batch_items = [
        {
            "id": "item-001",
            "text": "This product is amazing! Best purchase ever."
        },
        {
            "id": "item-002",
            "text": "Terrible experience. Would not recommend."
        },
        {
            "id": "item-003",
            "text": "Average product, nothing special but works."
        },
        {
            "id": "item-004",
            "text": "Exceeded expectations! Great value for money."
        },
        {
            "id": "item-005",
            "text": "Disappointed with the quality. Expected better."
        }
    ]
    
    flow_id = "sentiment-analysis"
    
    # Example 1: Sequential processing
    print("Example 1: Sequential Batch Processing")
    print("=" * 60)
    
    seq_results = batch_process_sequential(client, flow_id, batch_items)
    
    print(f"\nSequential Results:")
    print(f"  Total items: {seq_results['total_items']}")
    print(f"  Successful: {seq_results['successful']}")
    print(f"  Failed: {seq_results['failed']}")
    print(f"  Time elapsed: {seq_results['elapsed_time']:.2f} seconds")
    
    # Print individual results
    for item_id, result in seq_results["results"].items():
        if result["status"] == "success":
            print(f"  {item_id}: Success - {result.get('output')}")
        else:
            print(f"  {item_id}: Failed - {result.get('error')}")
    
    # Example 2: Parallel processing
    print("\n" + "=" * 60)
    print("Example 2: Parallel Batch Processing")
    print("=" * 60)
    
    par_results = batch_process_parallel(client, flow_id, batch_items, max_workers=3)
    
    print(f"\nParallel Results:")
    print(f"  Total items: {par_results['total_items']}")
    print(f"  Successful: {par_results['successful']}")
    print(f"  Failed: {par_results['failed']}")
    print(f"  Time elapsed: {par_results['elapsed_time']:.2f} seconds")
    print(f"  Speedup: {seq_results['elapsed_time'] / par_results['elapsed_time']:.2f}x")
    
    # Example 3: Batch with different flows
    print("\n" + "=" * 60)
    print("Example 3: Multi-Flow Batch Processing")
    print("=" * 60)
    
    multi_flow_items = [
        {
            "flow_id": "sentiment-analysis",
            "data": {"id": "multi-001", "text": "Great product!"}
        },
        {
            "flow_id": "credit-analysis",
            "data": {"id": "multi-002", "customer_id": "CUST-100", "amount": 10000}
        },
        {
            "flow_id": "text-summarization",
            "data": {"id": "multi-003", "text": "Long text to summarize..."}
        }
    ]
    
    multi_results = {}
    
    for item in multi_flow_items:
        flow_id = item["flow_id"]
        data = item["data"]
        item_id = data.get("id")
        
        print(f"Processing {item_id} with flow {flow_id}...")
        
        try:
            result = client.execute_and_wait(flow_id, data, timeout=60)
            multi_results[item_id] = {
                "flow": flow_id,
                "status": "success",
                "output": result.get("output_data")
            }
        except AISpineError as e:
            multi_results[item_id] = {
                "flow": flow_id,
                "status": "error",
                "error": str(e)
            }
    
    print("\nMulti-flow results:")
    for item_id, result in multi_results.items():
        print(f"  {item_id} ({result['flow']}): {result['status']}")
    
    # Clean up
    client.close()


if __name__ == "__main__":
    main()