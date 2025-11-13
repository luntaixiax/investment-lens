import { useRef, useEffect, useState } from 'react';

export function useClickOutside<T extends HTMLElement>(
    enabled: boolean = true
) {
    const dropdownRef = useRef<T>(null); // the user needs to pass in the ref of the element to listen to
    const [isOpen, setIsOpen] = useState(false);

    // this effect only runs when isOpen changes or enabled changes
    useEffect(() => {
        if (!enabled || !isOpen) {
            // if not enabled or not open, do nothing
            return;
        }
        // so it only listens to the mousedown event when the dropdown is OPEN!
        const handleClick = (event: MouseEvent) => {
            // if user clicks outside the element, close the dropdown by setting isOpen to false
            // which will trigger the useEffect again to remove the event listener
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        
        // when user clicks outside the element, add the event listener of mousedown to the document
        // which will trigger the handleClick function to close the dropdown
        document.addEventListener('mousedown', handleClick);
        // when the component unmounts, remove the event listener of mousedown from the document
        return () => document.removeEventListener('mousedown', handleClick);
    }, [isOpen, enabled]);

    return { dropdownRef, isOpen, setIsOpen };
}