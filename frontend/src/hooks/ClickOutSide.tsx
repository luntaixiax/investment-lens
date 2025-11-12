import { useRef, useEffect } from 'react';

export function useClickOutside<T extends HTMLElement>(
    callback: () => void,
    enabled: boolean = true
) {
    const ref = useRef<T>(null);

    useEffect(() => {
        if (!enabled) {
            return;
        }

        const handleClick = (event: MouseEvent) => {
            if (ref.current && !ref.current.contains(event.target as Node)) {
                callback();
            }
        };
        
        // when user clicks outside the element
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [callback, enabled]);

    return ref;
}